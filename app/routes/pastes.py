from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
import json

from app.services.storage import redis_client
from app.services.time import now_ms

router = APIRouter()

class PasteCreate(BaseModel):
    content: str
    ttl_seconds: Optional[int] = None
    max_views: Optional[int] = None

@router.post("/api/pastes")
def create_paste(payload: PasteCreate, request: Request):
    # Validation
    if not payload.content or not payload.content.strip():
        raise HTTPException(status_code=400, detail="content must be non-empty")

    if payload.ttl_seconds is not None and payload.ttl_seconds < 1:
        raise HTTPException(status_code=400, detail="ttl_seconds must be >= 1")

    if payload.max_views is not None and payload.max_views < 1:
        raise HTTPException(status_code=400, detail="max_views must be >= 1")

    paste_id = uuid4().hex
    created_at = now_ms(request)

    expires_at = None
    if payload.ttl_seconds:
        expires_at = created_at + payload.ttl_seconds * 1000

    paste_data = {
        "content": payload.content,
        "created_at": created_at,
        "expires_at": expires_at,
        "max_views": payload.max_views,
        "views": 0
    }

    key = f"paste:{paste_id}"
    redis_client.set(key, json.dumps(paste_data))

    # Redis TTL (optional)
    if payload.ttl_seconds:
        redis_client.expire(key, payload.ttl_seconds)

    base_url = str(request.base_url).rstrip("/")
    return {
        "id": paste_id,
        "url": f"{base_url}/p/{paste_id}"
    }

from fastapi import Path

@router.get("/api/pastes/{paste_id}")
def get_paste(
    paste_id: str = Path(..., min_length=1),
    request: Request = None
):
    key = f"paste:{paste_id}"
    raw = redis_client.get(key)

    if not raw:
        raise HTTPException(status_code=404, detail="Paste not found")

    paste = json.loads(raw)

    now = now_ms(request)

    # Check expiry
    if paste["expires_at"] is not None and now > paste["expires_at"]:
        redis_client.delete(key)
        raise HTTPException(status_code=404, detail="Paste expired")

    # Check view limit
    max_views = paste["max_views"]
    views = paste["views"]

    if max_views is not None and views >= max_views:
        raise HTTPException(status_code=404, detail="View limit exceeded")

    # Increment views
    paste["views"] += 1
    redis_client.set(key, json.dumps(paste))

    remaining_views = None
    if max_views is not None:
        remaining_views = max_views - paste["views"]

    return {
        "content": paste["content"],
        "remaining_views": remaining_views,
        "expires_at": (
            None if paste["expires_at"] is None
            else __import__("datetime")
                 .datetime.utcfromtimestamp(paste["expires_at"] / 1000)
                 .isoformat() + "Z"
        )
    }
