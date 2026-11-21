from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.request_timing import RequestTimingMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent
WEBSITE_DIR = BASE_DIR / "website"


def _website_page(filename: str) -> FileResponse:
    """Return a file from the bundled website, or a clean 404."""
    path = WEBSITE_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found.")
    return FileResponse(path)


def _wants_html(request: Request) -> bool:
    """True for browsers and link previews, false for API clients."""
    return "text/html" in request.headers.get("accept", "").lower()


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Email Verification API for validating email syntax, domain/MX records, "
            "disposable domains, role-based addresses, and optional SMTP deliverability. "
            "Built for direct use and RapidAPI Hub distribution. "
            "RapidAPI handles consumer keys and billing; the backend can additionally "
            "require X-RapidAPI-Proxy-Secret."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=settings.cors_methods or ["*"],
        allow_headers=settings.cors_headers or ["*"],
    )

    assets_dir = WEBSITE_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/", tags=["Root"], include_in_schema=False)
    async def root(request: Request):
        """Product website for browsers; service metadata for API clients."""
        if _wants_html(request) and (WEBSITE_DIR / "index.html").is_file():
            return FileResponse(WEBSITE_DIR / "index.html")
        return JSONResponse(
            {
                "service": settings.app_name,
                "version": settings.app_version,
                "website": "/",
                "docs": "/docs",
                "terms": "/terms",
                "privacy": "/privacy",
                "health": "/api/v1/health",
                "api": "/api/v1",
            }
        )

    @app.get("/terms", tags=["Website"], include_in_schema=False)
    async def terms() -> FileResponse:
        return _website_page("terms.html")

    @app.get("/privacy", tags=["Website"], include_in_schema=False)
    async def privacy() -> FileResponse:
        return _website_page("privacy.html")

    @app.get("/robots.txt", tags=["Website"], include_in_schema=False)
    async def robots() -> FileResponse:
        return _website_page("robots.txt")

    @app.get("/favicon.ico", tags=["Website"], include_in_schema=False)
    async def favicon() -> FileResponse:
        return _website_page("assets/favicon.svg")

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
