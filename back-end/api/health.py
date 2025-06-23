from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/health", tags=["Health"])


@router.get("/health-check")
def health():
    return {
        "status": "ok",
        "message": "Chat service is running",
        "version": "1.0.0"
    }