import json

import firebase_admin
from firebase_admin import auth as firebase_auth, credentials

from app.config import settings


def _ensure_app() -> None:
    if firebase_admin._apps:
        return
    if settings.firebase_service_account_json:
        cred = credentials.Certificate(json.loads(settings.firebase_service_account_json))
    elif settings.firebase_service_account_file:
        cred = credentials.Certificate(settings.firebase_service_account_file)
    else:
        cred = credentials.ApplicationDefault()
    options = {"projectId": settings.firebase_project_id} if settings.firebase_project_id else None
    firebase_admin.initialize_app(cred, options)


def verify_firebase_token(id_token: str) -> dict:
    _ensure_app()
    return firebase_auth.verify_id_token(id_token)
