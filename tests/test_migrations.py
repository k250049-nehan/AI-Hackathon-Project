"""Database migrations are real and reversible."""

import os
import tempfile

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.config import settings


def test_alembic_migration_creates_all_tables():
    path = os.path.join(tempfile.gettempdir(), "lastmile_pytest_migrations.db")
    if os.path.exists(path):
        os.remove(path)
    original = settings.database_url
    settings.database_url = "sqlite:///" + path
    try:
        cfg = Config(os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini"))
        command.upgrade(cfg, "head")
        tables = set(inspect(create_engine(settings.database_url)).get_table_names())
        assert {"users", "cases", "consents", "rule_sets", "audit_logs", "api_keys"} <= tables
        command.downgrade(cfg, "base")
        tables_after = set(inspect(create_engine(settings.database_url)).get_table_names())
        assert "cases" not in tables_after
        command.upgrade(cfg, "head")
        assert "cases" in set(inspect(create_engine(settings.database_url)).get_table_names())
    finally:
        settings.database_url = original
