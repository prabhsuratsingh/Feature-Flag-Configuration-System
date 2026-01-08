from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.database.db import SessionLocal
from app.models.client import Client
import hashlib

API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def require_api_key(
    api_key: str = Security(API_KEY_HEADER),
    db: Session = Depends(get_db),
):
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    hashed = hash_api_key(api_key)

    client = (
        db.query(Client)
        .filter(Client.api_key_hash == hashed, Client.is_active.is_(True))
        .first()
    )

    if not client:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return client
