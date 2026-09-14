"""Single async entrypoint for document ingestion. Populated in a later task."""

import logging
import uuid

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import AsyncSessionLocal
from app.db.postgres.models import (
    Chunk,
    Document,
    Entity,
    Equipment,
    EquipmentConnection,
    FailureMode,
    MaintenanceEvent,
    Regulation,
)
from app.pipeline.chunking import chunk_document
from app.pipeline.embedding import embed_and_store
from app.pipeline.entity_extraction import extract_entities, extract_llm_structured_data
from app.pipeline.form_extraction import is_structured_form, structure_form_page
from app.pipeline.llm_fallback_extraction import LLMFallbackResult
from app.pipeline.parsing import parse_document, ParsedLine
from app.pipeline.relationship_extraction import extract_relationships_cooccurrence
from app.pipeline.relationship_refinement import refine_relationships_llm
from app.pipeline.semantic_metadata import extract_semantic_metadata
from app.pipeline.spreadsheet_parsing import parse_spreadsheet, needs_spreadsheet_parsing
from app.pipeline.email_parsing import parse_email, needs_email_parsing
from app.services.graph_service import upsert_equipment
from app.services.search_service import bump_chunks_version

logger = logging.getLogger(__name__)


async def _update_status(db: AsyncSession, document: Document, status: str, error_message: str | None = None) -> None:
    document.upload_status = status
    if error_message is not None:
        document.error_message = error_message
    await db.commit()


async def _get_or_create_equipment(db: AsyncSession, tag_number: str) -> Equipment:
    return await upsert_equipment(db, tag_number=tag_number)


async def _get_or_create_regulation(db: AsyncSession, code: str) -> Regulation:
    stmt = (
        pg_insert(Regulation)
        .values(code=code, title=None, equipment_id=None)
        .on_conflict_do_nothing(index_elements=["code"])
        .returning(Regulation)
    )
    result = await db.execute(stmt)
    regulation = result.scalar_one_or_none()
    if regulation is not None:
        await db.flush()
        return regulation
    result = await db.execute(select(Regulation).where(Regulation.code == code))
    return result.scalars().first()


async def _clear_existing_ingestion_data(db: AsyncSession, document_id: uuid.UUID) -> None:
    """Delete rows from a prior ingestion of this document, so re-running
    ingest_document produces a clean rebuild instead of duplicates.
    Chunks cascade-delete their Entities via the existing FK (ondelete=CASCADE).
    Equipment and EquipmentConnection are intentionally NOT cleared — they are
    shared across documents and already use get-or-create dedup, so clearing
    them here would incorrectly affect data owned by other documents.
    Regulation is intentionally NOT touched here — it has no document_id column
    (it's deduplicated by code via _get_or_create_regulation instead, see Step 5 below).
    """
    await db.execute(delete(Chunk).where(Chunk.document_id == document_id))
    await db.execute(delete(MaintenanceEvent).where(MaintenanceEvent.document_id == document_id))
    await db.execute(delete(FailureMode).where(FailureMode.document_id == document_id))
    await db.flush()


async def _write_relations_to_postgres(
    db: AsyncSession,
    document: Document,
    chunks_data: list,
    entities: list,
    equipment_connections: list,
    regulation_links: list,
) -> list[Chunk]:
    # Step 1 — persist chunks
    chunk_index_to_chunk = {}
    for chunk_data in chunks_data:
        chunk = Chunk(
            document_id=document.id,
            chunk_index=chunk_data.chunk_index,
            content=chunk_data.content,
            page_number=chunk_data.page_number,
            bbox={"page_bbox": chunk_data.bbox} if chunk_data.bbox else None,
            section_title=chunk_data.section_title,
        )
        db.add(chunk)
        chunk_index_to_chunk[chunk_data.chunk_index] = chunk
    await db.flush()

    # Step 2 — persist entities and get-or-create equipment
    tag_to_equipment = {}
    for entity in entities:
        chunk = chunk_index_to_chunk[entity.chunk_index]
        db.add(
            Entity(
                chunk_id=chunk.id,
                entity_type=entity.entity_type,
                entity_text=entity.entity_text,
                normalized_value=entity.normalized_value,
                confidence=entity.confidence,
            )
        )
        if entity.entity_type == "equipment" and entity.normalized_value not in tag_to_equipment:
            tag_to_equipment[entity.normalized_value] = await _get_or_create_equipment(
                db, entity.normalized_value
            )
    await db.flush()

    # Step 3 — populate chunk.equipment_ids
    chunk_equipment_ids: dict[uuid.UUID, set[uuid.UUID]] = {}
    for entity in entities:
        if entity.entity_type == "equipment":
            chunk = chunk_index_to_chunk[entity.chunk_index]
            equipment = tag_to_equipment[entity.normalized_value]
            chunk_equipment_ids.setdefault(chunk.id, set()).add(equipment.id)

    chunk_id_to_obj = {chunk.id: chunk for chunk in chunk_index_to_chunk.values()}
    for chunk_id, equipment_ids in chunk_equipment_ids.items():
        chunk_id_to_obj[chunk_id].equipment_ids = list(equipment_ids)

    # Step 4 — persist equipment connections
    for conn in equipment_connections:
        a = tag_to_equipment.get(conn.equipment_tag_a)
        b = tag_to_equipment.get(conn.equipment_tag_b)
        if a is None or b is None:
            logger.warning(
                f"Skipping equipment connection: missing equipment for tags "
                f"{conn.equipment_tag_a} or {conn.equipment_tag_b}"
            )
            continue
        result = await db.execute(
            select(EquipmentConnection).where(
                or_(
                    and_(
                        EquipmentConnection.equipment_id == a.id,
                        EquipmentConnection.connected_equipment_id == b.id,
                    ),
                    and_(
                        EquipmentConnection.equipment_id == b.id,
                        EquipmentConnection.connected_equipment_id == a.id,
                    ),
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            db.add(
                EquipmentConnection(
                    equipment_id=a.id,
                    connected_equipment_id=b.id,
                    relation_type="physical",
                )
            )

    # Step 5 — persist regulation links
    for link in regulation_links:
        equipment = tag_to_equipment.get(link.equipment_tag)
        if equipment is None:
            logger.warning(
                f"Skipping regulation link: missing equipment for tag {link.equipment_tag}"
            )
            continue
        regulation = await _get_or_create_regulation(db, link.regulation_code)
        regulation.equipment_id = equipment.id

    await db.commit()
    return list(chunk_index_to_chunk.values())


async def _write_llm_fallback_results(
    db: AsyncSession,
    document_id: uuid.UUID,
    llm_results: dict[int, LLMFallbackResult],
) -> None:
    try:
        for result in llm_results.values():
            for fm in result.failure_modes:
                db.add(
                    FailureMode(
                        description=fm.description,
                        category=fm.category,
                        document_id=document_id,
                        equipment_id=None,
                    )
                )
            for me in result.maintenance_events:
                db.add(
                    MaintenanceEvent(
                        action=me.action,
                        event_date=None,
                        document_id=document_id,
                        equipment_id=None,
                        addressed_failure_id=None,
                    )
                )
            for reg_code in result.regulations:
                await _get_or_create_regulation(db, reg_code)
        await db.flush()
    except Exception as exc:
        logger.warning(f"LLM fallback persistence failed: {exc}")
        await db.rollback()
        return


async def _write_semantic_metadata(
    db: AsyncSession,
    document: Document,
    chunks_data: list,
) -> None:
    try:
        result = await extract_semantic_metadata(chunks_data)
        document.summary = result.summary
        document.primary_equipment = result.primary_equipment
        document.revision = result.revision
        await db.flush()
    except Exception as exc:
        logger.warning(f"Semantic metadata persistence failed: {exc}")
        await db.rollback()
        return


async def ingest_document(document_id: uuid.UUID) -> None:
    async with AsyncSessionLocal() as db:
        document = None
        try:
            result = await db.execute(select(Document).where(Document.id == document_id))
            document = result.scalar_one_or_none()
            if document is None:
                logger.error(f"Document {document_id} not found")
                return

            await _clear_existing_ingestion_data(db, document.id)
            await _update_status(db, document, "ocr")
            if needs_email_parsing(document.file_path):
                parsed_pages = parse_email(document.file_path)
            elif needs_spreadsheet_parsing(document.file_path):
                parsed_pages = parse_spreadsheet(document.file_path)
            else:
                parsed_pages = await parse_document(document.file_path)

            # Detect and restructure form-style pages
            for page in parsed_pages:
                if is_structured_form(page.text):
                    page.text = structure_form_page(page.text, page.page_number)
                    page.lines = [ParsedLine(text=line, font_size=None) for line in page.text.splitlines()]

            await _update_status(db, document, "extracting")
            chunks_data = chunk_document(parsed_pages)
            entities = await extract_entities(chunks_data)
            llm_results = await extract_llm_structured_data(chunks_data)
            equipment_connections, regulation_links = extract_relationships_cooccurrence(entities)
            equipment_connections, regulation_links = await refine_relationships_llm(
                equipment_connections, regulation_links, chunks_data
            )
            persisted_chunks = await _write_relations_to_postgres(
                db, document, chunks_data, entities, equipment_connections, regulation_links
            )
            await _write_llm_fallback_results(db, document.id, llm_results)
            await _write_semantic_metadata(db, document, chunks_data)
            await _update_status(db, document, "embedding")
            await embed_and_store(document, persisted_chunks)
            await db.commit()
            await _update_status(db, document, "ready")
            bump_chunks_version()
            logger.info(f"Ingestion completed for document_id={document_id}")
        except Exception as e:
            logger.exception(f"Ingestion failed for document_id={document_id}")
            try:
                await db.rollback()
                if document is not None:
                    await _update_status(db, document, "failed", error_message=str(e))
            except Exception:
                logger.exception(
                    f"Failed to record failure status for document_id={document_id} "
                    f"after rollback — document may be left in a stale status"
                )
            return
