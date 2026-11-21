import hmac
from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


def _secret_matches(provided: Optional[str], expected: str) -> bool:
    """Constant-time comparison that tolerates missing/non-ASCII headers."""
    if not provided:
        return False
    return hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))


async def verify_api_access(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    x_rapidapi_proxy_secret: Optional[str] = Header(default=None, alias="X-RapidAPI-Proxy-Secret"),
    x_rapidapi_key: Optional[str] = Header(default=None, alias="X-RapidAPI-Key"),
    x_rapidapi_host: Optional[str] = Header(default=None, alias="X-RapidAPI-Host"),
) -> None:
    """Validate request authentication for direct and RapidAPI usage.

    Behavior:
    - If RAPIDAPI_PROXY_SECRET is configured, requests must include a matching
      X-RapidAPI-Proxy-Secret header. RapidAPI injects this header at the gateway;
      consumers never send it themselves.
    - If API_KEY is configured, requests must include a matching X-API-Key header.
    - If neither is configured, authentication checks are skipped (useful for local dev).
    - Presence of X-RapidAPI-Key / X-RapidAPI-Host is accepted as a signal of RapidAPI
      traffic but is not treated as a secret by itself.
    """
    settings = get_settings()

    if settings.rapidapi_proxy_secret and not _secret_matches(
        x_rapidapi_proxy_secret, settings.rapidapi_proxy_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing RapidAPI proxy secret.",
        )

    if settings.api_key and not _secret_matches(x_api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )

    # RapidAPI adds these headers to proxied consumer traffic. They identify the
    # marketplace request but are not backend secrets, so no validation is needed.
    _ = (x_rapidapi_key, x_rapidapi_host)
    return None
