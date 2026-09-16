import os
from pathlib import Path

import httpx

from app.config import settings

LOCAL_PREFIX = "local://"
SUPABASE_PREFIX = "supabase://"


def _cloud_configured() -> bool:
    return bool(settings.supabase_url and settings.supabase_service_role_key)


def _object_url(key: str) -> str:
    return f"{settings.supabase_url}/storage/v1/object/{settings.supabase_storage_bucket}/{key}"


def _auth_headers() -> dict:
    # Both headers on purpose: Supabase's newer opaque "secret key" format
    # (sb_secret_...) is only accepted via the apikey header - sent as a
    # Bearer token it 400s with "Invalid Compact JWS", since that path
    # expects an actual JWT. The legacy service_role key *is* a JWT and
    # works fine as a Bearer token, so keep sending both for compatibility
    # with either key format.
    key = settings.supabase_service_role_key
    return {"apikey": key, "Authorization": f"Bearer {key}"}


async def save_document_bytes(document_id, content: bytes) -> str:
    """
    Persist an uploaded document's bytes and return an opaque key to store as
    Document.file_path. Render's free tier has no persistent disk, so local
    storage doesn't survive a restart in production - this uses Supabase
    Storage when configured, and falls back to local disk so it still works
    for local development without any cloud credentials set up.
    """
    key = f"{document_id}.pdf"
    if _cloud_configured():
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                _object_url(key), headers=_auth_headers(), content=content, timeout=60.0
            )
            resp.raise_for_status()
        return f"{SUPABASE_PREFIX}{key}"

    os.makedirs(settings.upload_dir, exist_ok=True)
    dest_path = Path(settings.upload_dir) / key
    dest_path.write_bytes(content)
    return f"{LOCAL_PREFIX}{dest_path}"


async def download_to_local_path(stored_key: str, local_dest: str) -> None:
    """Fetch a document previously saved via save_document_bytes down to a real
    local file path, for the pipeline code that needs to open() it directly."""
    if stored_key.startswith(SUPABASE_PREFIX):
        key = stored_key[len(SUPABASE_PREFIX):]
        async with httpx.AsyncClient() as client:
            resp = await client.get(_object_url(key), headers=_auth_headers(), timeout=60.0)
            resp.raise_for_status()
        Path(local_dest).write_bytes(resp.content)
        return

    if stored_key.startswith(LOCAL_PREFIX):
        source_path = stored_key[len(LOCAL_PREFIX):]
    else:
        # Rows written before storage_service existed stored a bare local path.
        source_path = stored_key
    Path(local_dest).write_bytes(Path(source_path).read_bytes())
