from collections.abc import Generator
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError, InterfaceError, OperationalError, ProgrammingError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config.settings import settings
from app.core.exception.errors import DatabaseConnectionError


logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def log_database_target() -> None:
    target = settings.sanitized_db_target
    logger.info(
        "Database target host=%s port=%s database=%s user=%s",
        target["host"],
        target["port"],
        target["database"],
        target["username"],
    )


def probe_database_connection() -> None:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        target = settings.sanitized_db_target
        logger.exception(
            "Database connectivity probe failed host=%s port=%s database=%s user=%s",
            target["host"],
            target["port"],
            target["database"],
            target["username"],
        )
        raise DatabaseConnectionError("Unable to connect to the configured database.") from exc


def database_is_available() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    return True


def is_database_connectivity_error(exc: BaseException) -> bool:
    if isinstance(exc, (OperationalError, InterfaceError)):
        return True
    if isinstance(exc, DBAPIError) and exc.connection_invalidated:
        return True

    message = str(exc).lower()
    markers = (
        "could not connect",
        "connection refused",
        "connection reset",
        "connection is closed",
        "server closed the connection",
        "could not translate host name",
        "timeout expired",
        "password authentication failed",
        "role \"",
        "authentication failed",
    )
    return any(marker in message for marker in markers)


def is_database_schema_error(exc: BaseException) -> bool:
    if isinstance(exc, ProgrammingError):
        return True

    dbapi_error = exc if isinstance(exc, DBAPIError) else None
    if dbapi_error is not None and getattr(dbapi_error, "orig", None) is not None:
        orig_name = dbapi_error.orig.__class__.__name__.lower()
        if orig_name in {"undefinedcolumn", "undefinedtable", "undefinedfunction", "datatypemismatch"}:
            return True

    message = str(exc).lower()
    markers = (
        "undefinedcolumn",
        "undefined table",
        "no such column",
        " does not exist",
    )
    return any(marker in message for marker in markers)
