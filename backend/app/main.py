"""
FastAPI application entrypoint.

Run with:  uvicorn app.main:app --reload --port 8000
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router as api_router
from app.core.config import get_settings
from app.core.exceptions import AssistantError
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Real-time Audio-In Audio-Out Conversational AI Assistant API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.exception_handler(AssistantError)
async def assistant_error_handler(request: Request, exc: AssistantError) -> JSONResponse:
    """Catch-all for our custom exception hierarchy -> clean JSON error response."""
    logger.error("Unhandled AssistantError on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running. See /docs for API docs."}
