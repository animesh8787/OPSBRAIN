import uuid

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres.models import Equipment, EquipmentConnection
from app.schemas import EquipmentConnectionItem, EquipmentNeighborhoodItem

EQUIPMENT_NEIGHBORHOOD_QUERY = text("""
    WITH RECURSIVE connected AS (
        SELECT id, tag_number, 0 AS depth FROM equipment WHERE tag_number = :tag
        UNION
        SELECT e.id, e.tag_number, c.depth + 1
        FROM equipment e
        JOIN equipment_connections ec ON ec.connected_equipment_id = e.id
        JOIN connected c ON ec.equipment_id = c.id
        WHERE c.depth < :max_depth
    )
    SELECT c.tag_number,
           array_agg(DISTINCT f.description) AS failures,
           array_agg(DISTINCT r.code) AS regulations
    FROM connected c
    LEFT JOIN failure_modes f ON f.equipment_id = c.id
    LEFT JOIN regulations r ON r.equipment_id = c.id
    GROUP BY c.tag_number
""")

_EQUIPMENT_NEIGHBORHOOD_IDS_QUERY = text("""
    WITH RECURSIVE connected AS (
        SELECT id, tag_number, 0 AS depth FROM equipment WHERE tag_number = :tag
        UNION
        SELECT e.id, e.tag_number, c.depth + 1
        FROM equipment e
        JOIN equipment_connections ec ON ec.connected_equipment_id = e.id
        JOIN connected c ON ec.equipment_id = c.id
        WHERE c.depth < :max_depth
    )
    SELECT id, tag_number FROM connected
""")


def _clean_agg_array(values: list | None) -> list[str]:
    if values is None:
        return []
    return [v for v in values if v is not None]


async def get_equipment_neighborhood(db: AsyncSession, tag: str, max_depth: int) -> list[EquipmentNeighborhoodItem]:
    result = await db.execute(EQUIPMENT_NEIGHBORHOOD_QUERY, {"tag": tag, "max_depth": max_depth})
    rows = result.fetchall()
    if not rows:
        return []
    return [
        EquipmentNeighborhoodItem(
            tag_number=row.tag_number,
            failures=_clean_agg_array(row.failures),
            regulations=_clean_agg_array(row.regulations),
        )
        for row in rows
    ]


async def _get_equipment_connections(
    db: AsyncSession, equipment_ids: list[uuid.UUID]
) -> list[EquipmentConnectionItem]:
    if not equipment_ids:
        return []

    e1 = Equipment.__table__.alias("e1")
    e2 = Equipment.__table__.alias("e2")

    stmt = (
        select(e1.c.tag_number.label("from_tag"), e2.c.tag_number.label("to_tag"))
        .select_from(EquipmentConnection.__table__)
        .join(e1, EquipmentConnection.equipment_id == e1.c.id)
        .join(e2, EquipmentConnection.connected_equipment_id == e2.c.id)
        .where(
            EquipmentConnection.equipment_id.in_(equipment_ids),
            EquipmentConnection.connected_equipment_id.in_(equipment_ids),
        )
    )

    result = await db.execute(stmt)
    rows = result.fetchall()

    seen = set()
    connections = []
    for row in rows:
        pair = tuple(sorted((row.from_tag, row.to_tag)))
        if pair not in seen:
            seen.add(pair)
            connections.append(EquipmentConnectionItem(from_tag=pair[0], to_tag=pair[1]))

    return connections


async def get_equipment_neighborhood_with_connections(
    db: AsyncSession, tag: str, max_depth: int
) -> tuple[list[EquipmentNeighborhoodItem], list[EquipmentConnectionItem]]:
    equipment = await get_equipment_neighborhood(db, tag, max_depth)

    result = await db.execute(
        _EQUIPMENT_NEIGHBORHOOD_IDS_QUERY, {"tag": tag, "max_depth": max_depth}
    )
    id_tag_rows = result.fetchall()
    equipment_ids = [row.id for row in id_tag_rows]

    connections = await _get_equipment_connections(db, equipment_ids)

    return equipment, connections


async def upsert_equipment(
    db: AsyncSession,
    tag_number: str,
    name: str | None = None,
    equipment_type: str | None = None,
    location: str | None = None,
) -> Equipment:
    """Idempotent upsert for an equipment row.

    Uses PostgreSQL ON CONFLICT to avoid duplicate rows when the same
    tag_number is inserted concurrently.
    """
    stmt = pg_insert(Equipment).values(
        tag_number=tag_number,
        name=name,
        equipment_type=equipment_type,
        location=location,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["tag_number"],
        set_={
            "name": stmt.excluded.name,
            "equipment_type": stmt.excluded.equipment_type,
            "location": stmt.excluded.location,
        },
    ).returning(Equipment)

    result = await db.execute(stmt)
    return result.scalar_one()
