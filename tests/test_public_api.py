"""Public REST API: API keys, scopes, docs, revocation and rate limiting."""

from app.config import settings


def _create_key(client, h):
    response = client.post(
        "/api/admin/api-keys",
        headers=h,
        json={"name": "judge-key", "scopes": ["cases:read", "cases:write"]},
    )
    assert response.status_code == 201, response.text
    return response.json()["plain_key"]


def test_api_key_is_mandatory(client):
    response = client.get("/api/public/whoami")
    assert response.status_code == 401
    assert response.json()["error"] == "api_key_required"


def test_api_key_identity_and_scope_enforcement(client, headers):
    key = _create_key(client, headers("admin"))
    who = client.get("/api/public/whoami", headers={"X-API-Key": key})
    assert who.status_code == 200
    assert who.json()["scopes"] == ["cases:read", "cases:write"]

    denied = client.post(
        "/api/public/classify",
        headers={"X-API-Key": key},
        json={"text": "hello"},
    )
    assert denied.status_code == 403
    assert denied.json()["error"] == "scope_denied"


def test_public_case_create_and_read(client, headers):
    key = _create_key(client, headers("admin"))
    h = {"X-API-Key": key}
    created = client.post(
        "/api/public/cases",
        headers=h,
        json={"subject_user_id": "user_admin_nadia", "raw_text": "relief claim via public api"},
    )
    assert created.status_code == 201, created.text
    case_id = created.json()["id"]
    fetched = client.get(f"/api/public/cases/{case_id}", headers=h)
    assert fetched.status_code == 200
    listed = client.get("/api/public/cases", headers=h)
    assert case_id in [item["id"] for item in listed.json()]


def test_revoked_key_stops_working(client, headers):
    key = _create_key(client, headers("admin"))
    keys = client.get("/api/admin/api-keys", headers=headers("admin")).json()
    created = next(item for item in keys if item["name"] == "judge-key")
    assert client.post(f"/api/admin/api-keys/{created['id']}/revoke", headers=headers("admin")).status_code == 200
    response = client.get("/api/public/whoami", headers={"X-API-Key": key})
    assert response.status_code == 401
    assert response.json()["error"] == "invalid_api_key"


def test_openapi_documentation_is_published(client):
    spec = client.get("/openapi.json")
    assert spec.status_code == 200
    paths = spec.json()["paths"]
    assert "/api/public/cases" in paths
    assert "/api/auth/login" in paths
    assert "/api/rules/digital-twin/simulate" in paths
    assert client.get("/docs").status_code == 200


def test_rate_limit_returns_429(client, headers):
    h = dict(headers("citizen"))
    h["X-Client-Id"] = "rate-limit-test-client"
    original = settings.rate_limit_per_min
    settings.rate_limit_per_min = 2
    try:
        codes = [client.get("/api/rules/active", headers=h).status_code for _ in range(4)]
        assert 429 in codes
        assert codes[:2] == [200, 200]
    finally:
        settings.rate_limit_per_min = original
