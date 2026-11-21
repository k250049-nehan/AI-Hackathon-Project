"""Test fixtures: a fresh seeded database and client for every test."""

import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.gettempdir(), "lastmile_test_suite.db")
os.environ["AUTO_SEED"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db as db_module
from app.config import settings
from app.data.seed import PASSWORD, seed_database
from app.db import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


@pytest.fixture()
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestSession()
    seed_database(session)
    original_session_local = db_module.SessionLocal
    db_module.SessionLocal = TestSession
    yield session
    session.close()
    db_module.SessionLocal = original_session_local


@pytest.fixture()
def client(db):
    def override_get_db():
        session = TestSession()
        try:
            yield session
        finally:
            session.close()

    previous_limit = settings.rate_limit_per_min
    settings.rate_limit_per_min = 10000
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()
    test_client.close()
    settings.rate_limit_per_min = previous_limit


def login(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/auth/login", json={"email": email, "password": PASSWORD}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


EMAILS = {
    "citizen": "fatima@mock.local",
    "citizen2": "ahmed@mock.local",
    "helper": "helper@mock.local",
    "officer": "officer@mock.local",
    "admin": "admin@mock.local",
    "auditor": "auditor@mock.local",
    "other_citizen": "zainab@mock.local",
    "other_helper": "helper2@mock.local",
    "other_officer": "officer2@mock.local",
    "other_admin": "admin2@mock.local",
}


@pytest.fixture()
def headers(client):
    def build(role: str) -> dict:
        return {"Authorization": "Bearer " + login(client, EMAILS[role])}

    return build
