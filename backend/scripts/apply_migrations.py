from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.database.session import engine, log_database_target, probe_database_connection


MIGRATIONS_DIR = BACKEND_ROOT / "migrations"

CREATE_MIGRATION_TABLE_SQL = text(
    """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        filename TEXT PRIMARY KEY,
        checksum TEXT NOT NULL,
        applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """
)

FETCH_APPLIED_SQL = text("SELECT filename, checksum FROM schema_migrations")
INSERT_APPLIED_SQL = text(
    "INSERT INTO schema_migrations (filename, checksum) VALUES (:filename, :checksum)"
)


def read_migration_files() -> list[Path]:
    if not MIGRATIONS_DIR.exists():
        raise RuntimeError(f"Migrations directory not found: {MIGRATIONS_DIR}")
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def checksum_for(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_tracking_table() -> None:
    with engine.begin() as connection:
        connection.execute(CREATE_MIGRATION_TABLE_SQL)


def fetch_applied() -> dict[str, str]:
    with engine.connect() as connection:
        rows = connection.execute(FETCH_APPLIED_SQL).all()
    return {filename: checksum for filename, checksum in rows}


def apply_single_migration(path: Path, checksum: str) -> None:
    sql_content = path.read_text(encoding="utf-8")
    with engine.begin() as connection:
        connection.exec_driver_sql(sql_content)
        connection.execute(
            INSERT_APPLIED_SQL,
            {"filename": path.name, "checksum": checksum},
        )


def main() -> int:
    try:
        log_database_target()
        probe_database_connection()
        ensure_tracking_table()
    except Exception as exc:  # noqa: BLE001
        print(f"Migration bootstrap failed: {exc}", file=sys.stderr)
        return 1

    try:
        migration_files = read_migration_files()
        applied = fetch_applied()
    except Exception as exc:  # noqa: BLE001
        print(f"Unable to load migration state: {exc}", file=sys.stderr)
        return 1

    for migration in migration_files:
        checksum = checksum_for(migration)
        applied_checksum = applied.get(migration.name)

        if applied_checksum:
            if applied_checksum != checksum:
                print(
                    f"Checksum mismatch for already-applied migration {migration.name}.",
                    file=sys.stderr,
                )
                return 1
            print(f"Skipping {migration.name} (already applied)")
            continue

        print(f"Applying {migration.name} ...")
        try:
            apply_single_migration(migration, checksum)
        except SQLAlchemyError as exc:
            print(f"Failed to apply {migration.name}: {exc}", file=sys.stderr)
            return 1

    print("Migrations complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
