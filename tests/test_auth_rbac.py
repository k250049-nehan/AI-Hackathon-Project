"""Authentication and server-side role-based access control."""


def test_login_success_and_profile(client, headers):
    h = headers("citizen")
    response = client.get("/api/auth/me", headers=h)
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "citizen"
    assert body["tenant_id"] == "tenant_relief_dept"


def test_login_rejects_bad_password(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "fatima@mock.local", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "invalid_credentials"


def test_missing_and_invalid_tokens_are_rejected(client):
    assert client.get("/api/dashboard").status_code == 401
    response = client.get(
        "/api/dashboard", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_citizen_cannot_publish_rules(client, headers):
    response = client.post(
        "/api/rules",
        headers=headers("citizen"),
        json={"definition": {"max_income": 100}, "change_note": "sneaky"},
    )
    assert response.status_code == 403
    assert response.json()["error"] == "role_denied"


def test_citizen_and_helper_cannot_review_claims(client, headers):
    case_id = client.get("/api/cases", headers=headers("citizen")).json()[0]["id"]
    for role in ("citizen", "helper"):
        response = client.post(
            f"/api/cases/{case_id}/review",
            headers=headers(role),
            json={"decision": "approved", "note": "self approve"},
        )
        assert response.status_code == 403


def test_auditor_is_read_only(client, headers):
    response = client.post(
        "/api/cases",
        headers=headers("auditor"),
        json={"raw_text": "relief claim"},
    )
    assert response.status_code == 403
    audit = client.get("/api/audit", headers=headers("auditor"))
    assert audit.status_code == 200
    assert isinstance(audit.json(), list)


def test_officer_queue_visible_to_officer_not_citizen(client, headers):
    assert client.get("/api/officer/queue", headers=headers("officer")).status_code == 200
    assert client.get("/api/officer/queue", headers=headers("citizen")).status_code == 403


def test_wrong_role_denied_details_are_explicit(client, headers):
    response = client.post(
        "/api/rules",
        headers=headers("helper"),
        json={"definition": {"max_income": 100}},
    )
    assert response.status_code == 403
    assert response.json()["details"]["required_roles"] == ["admin"]
