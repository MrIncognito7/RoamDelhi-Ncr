import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only-0123456789")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import get_db
from main import app
from models import Base


@pytest.fixture()
def client():
    # Fresh in-memory database per test, so tests never touch roam.db
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


USER = {"name": "Asha", "email": "Asha@Example.com", "password": "secret123"}


def test_register_returns_token_and_user(client):
    r = client.post("/register", json=USER)
    assert r.status_code == 201
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "asha@example.com"  # lower-cased
    assert "password" not in str(body)


def test_duplicate_email_rejected_case_insensitive(client):
    client.post("/register", json=USER)
    r = client.post("/register", json={**USER, "email": "asha@example.com"})
    assert r.status_code == 400


@pytest.mark.parametrize(
    "bad",
    [
        {"email": "not-an-email"},
        {"password": "short"},
        {"password": "x" * 73},
        {"name": "   "},
    ],
)
def test_register_validation(client, bad):
    r = client.post("/register", json={**USER, **bad})
    assert r.status_code == 422


def test_login_ok_and_email_case_insensitive(client):
    client.post("/register", json=USER)
    r = client.post("/login", json={"email": "ASHA@example.com", "password": "secret123"})
    assert r.status_code == 200
    assert r.json()["user"]["name"] == "Asha"


def test_login_wrong_password_and_unknown_email_same_message(client):
    client.post("/register", json=USER)
    wrong = client.post("/login", json={"email": "asha@example.com", "password": "nope-nope"})
    unknown = client.post("/login", json={"email": "who@example.com", "password": "secret123"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_me_with_and_without_token(client):
    token = client.post("/register", json=USER).json()["access_token"]
    ok = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200 and ok.json()["email"] == "asha@example.com"

    assert client.get("/me").status_code in (401, 403)  # no header
    bad = client.get("/me", headers={"Authorization": "Bearer garbage"})
    assert bad.status_code == 401


def test_expired_token_rejected(client):
    import jwt as pyjwt
    from datetime import datetime, timedelta, timezone
    from security import ALGORITHM, SECRET_KEY

    client.post("/register", json=USER)
    expired = pyjwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(seconds=5)},
        SECRET_KEY, algorithm=ALGORITHM,
    )
    r = client.get("/me", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401


def test_spots_still_public(client):
    assert client.get("/").json() == {"status": "ok"}
