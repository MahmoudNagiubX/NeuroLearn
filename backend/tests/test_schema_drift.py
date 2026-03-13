from __future__ import annotations

from sqlalchemy import text

from app.core.database.session import SessionLocal


def test_app_events_has_expected_columns() -> None:
    required_columns = {
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
    }

    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'app_events'
                """
            )
        ).scalars().all()
        columns = set(rows)

    assert required_columns.issubset(columns)


def test_app_events_metadata_is_non_nullable_with_default() -> None:
    with SessionLocal() as db:
        row = db.execute(
            text(
                """
                SELECT is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'app_events'
                  AND column_name = 'metadata'
                """
            )
        ).one()

    is_nullable, column_default = row
    assert is_nullable == "NO"
    assert column_default is not None
    assert "{}" in column_default


def test_schema_migrations_contains_app_events_expansion() -> None:
    with SessionLocal() as db:
        filenames = set(db.execute(text("SELECT filename FROM schema_migrations")).scalars().all())

    assert "004_expand_app_events_columns.sql" in filenames
