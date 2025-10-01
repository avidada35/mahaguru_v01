from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette import status as http_status
import logging
import uuid

from app.api.v1.api import api_router
from app.api.v1.studentgpt import router as studentgpt_router
from app.core.config import settings
import logging

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Mahaguru AI API - AI-powered learning platform",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Configure structured logging on startup
@app.on_event("startup")
async def on_startup() -> None:
    configure_logging()
    logging.getLogger(__name__).info("Application startup", extra={"props": {"env": settings.ENV}})


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logging.getLogger(__name__).info("Application shutdown")


# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Simple middleware: add request_id, enforce size limits, and set security headers
@app.middleware("http")
async def add_request_context_and_security(request: Request, call_next):
    # Assign request_id for tracing
    request.state.request_id = str(uuid.uuid4())

    # Enforce request body size limit if Content-Length provided
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > settings.MAX_REQUEST_BODY_BYTES:
                return JSONResponse(
                    status_code=http_status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "detail": "Request body too large",
                        "max_bytes": settings.MAX_REQUEST_BODY_BYTES,
                    },
                )
        except ValueError:
            pass

    response = await call_next(request)

    # Basic security headers
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    return response


# Consistent error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.getLogger(__name__).warning("Validation error", exc_info=False)
    return JSONResponse(
        status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.getLogger(__name__).error("Unhandled exception", exc_info=True)
    return JSONResponse(
        status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)
## StudentGPT router now included via api_router


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
