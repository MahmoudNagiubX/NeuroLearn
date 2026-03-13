from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config.settings import settings
from app.core.database.session import engine, log_database_target, probe_database_connection


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate database connectivity and required tables.")
    parser.add_argument(
        "--require-tables",
        default="",
        help="Comma-separated list of table names that must exist in public schema.",
    )
    parser.add_argument(
        "--check-events-schema",
        action="store_true",
        help="Verify app_events contains the expected tracking columns.",
    )
    return parser.parse_args()


def table_exists(table_name: str) -> bool:
    query = text("SELECT to_regclass(:table_name)")
    with engine.connect() as connection:
        result = connection.execute(query, {"table_name": f"public.{table_name}"}).scalar_one()
    return result is not None


def missing_columns(table_name: str, required_columns: list[str]) -> list[str]:
    query = text(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = :table_name
        """
    )
    with engine.connect() as connection:
        rows = connection.execute(query, {"table_name": table_name}).scalars().all()
    existing = set(rows)
    return [column for column in required_columns if column not in existing]


def main() -> int:
    args = parse_args()

    try:
        print("DB target:", settings.sanitized_db_target)
        log_database_target()
        probe_database_connection()
    except Exception as exc:  # noqa: BLE001
        print(f"Database connection failed: {exc}", file=sys.stderr)
        return 1

    required_tables = [item.strip() for item in args.require_tables.split(",") if item.strip()]
    if required_tables:
        missing: list[str] = []
        try:
            for table_name in required_tables:
                if not table_exists(table_name):
                    missing.append(table_name)
        except SQLAlchemyError as exc:
            print(f"Failed to verify required tables: {exc}", file=sys.stderr)
            return 1

        if missing:
            print(f"Missing required tables: {', '.join(missing)}", file=sys.stderr)
            return 1

    if args.check_events_schema:
        required_event_columns = [
            "id",
            "user_id",
            "event_type",
            "entity_type",
            "entity_id",
            "subject_id",
            "task_id",
            "study_session_id",
            "pomodoro_session_id",
            "note_id",
            "metadata",
            "occurred_at",
            "created_at",
        ]
        try:
            missing_event_columns = missing_columns("app_events", required_event_columns)
        except SQLAlchemyError as exc:
            print(f"Failed to validate app_events schema: {exc}", file=sys.stderr)
            return 1
        if missing_event_columns:
            print(
                "app_events schema mismatch. Missing columns: "
                + ", ".join(missing_event_columns),
                file=sys.stderr,
            )
            return 1

    print("Database connectivity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
