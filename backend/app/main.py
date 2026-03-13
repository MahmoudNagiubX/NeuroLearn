import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.analytics import router as analytics_router
from app.api.routes.auth import router as auth_router
from app.api.routes.events import router as events_router
from app.api.routes.notes import router as notes_router
from app.api.routes.pomodoro import router as pomodoro_router
from app.api.routes.study_sessions import router as study_sessions_router
from app.api.routes.subjects import router as subjects_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.users import router as users_router
from app.core.config.settings import settings
from app.core.database.session import (
    database_is_available,
    is_database_connectivity_error,
    is_database_schema_error,
    log_database_target,
    probe_database_connection,
)
from app.core.exception.errors import DatabaseConnectionError
from app.core.logging.logger import configure_logging


configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    log_database_target()
    try:
        probe_database_connection()
    except DatabaseConnectionError as exc:
        logger.error("Application startup aborted because database validation failed.")
        raise RuntimeError("Database startup validation failed.") from exc
    yield


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database error on %s %s", request.method, request.url.path)
    if is_database_connectivity_error(exc):
        return JSONResponse(
            status_code=503,
            content={"detail": "Database is unavailable. Please try again later."},
        )
    if is_database_schema_error(exc):
        return JSONResponse(
            status_code=500,
            content={"detail": "Database schema mismatch detected. Apply latest migrations."},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Database operation failed."},
    )


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": f"{settings.APP_NAME} is alive"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
def db_health_check() -> dict[str, str]:
    if not database_is_available():
        raise HTTPException(status_code=503, detail="Database is unavailable.")
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(subjects_router)
app.include_router(tasks_router)
app.include_router(study_sessions_router)
app.include_router(pomodoro_router)
app.include_router(notes_router)
app.include_router(events_router, prefix="/events", tags=["events"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
