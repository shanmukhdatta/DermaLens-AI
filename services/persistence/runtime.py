"""Database configuration; migrations are never silently created on startup."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker


def build_database(url: str) -> tuple[Engine, sessionmaker[Session]]:
    if not url.startswith(("postgresql+psycopg://", "sqlite+pysqlite://")):
        raise ValueError("Only PostgreSQL (or SQLite for tests) is supported")
    engine = create_engine(url, pool_pre_ping=True, future=True)
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(connection: Any, record: Any) -> None:
            del record
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine, sessionmaker(bind=engine, expire_on_commit=False)
