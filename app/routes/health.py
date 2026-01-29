from fastapi import APIRouter
from app.services.storage import redis_client

router = APIRouter()

@router.get("/api/healthz")
def healthz():
    try:
        redis_client.ping()
        return {"ok": True}
    except Exception:
        return {"ok": False}
