from typing import Dict

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.email import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """Return basic service health information."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.get("/ping", summary="Ping")
async def ping() -> Dict[str, str]:
    """Simple liveness endpoint."""
    return {"message": "pong"}
