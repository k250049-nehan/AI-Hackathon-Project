"""Multi-tenant isolation enforced on the server."""

TENANT1_CASE_SUBJECT = "user_citizen_fatima"


def test_other_tenant_cannot_read_cases(client, headers):
    case_id = client.get("/api/cases", headers=headers("citizen")).json()[0]["id"]
    for role in ("other_helper", "other_officer", "other_admin", "other_citizen"):
        response = client.get(f"/api/cases/{case_id}", headers=headers(role))
        assert response.status_code == 404, (role, response.text)


def test_other_tenant_cannot_create_case_for_foreign_subject(client, headers):
    response = client.post(
        "/api/cases",
        headers=headers("other_helper"),
        json={"subject_user_id": TENANT1_CASE_SUBJECT, "raw_text": "relief claim"},
    )
    assert response.status_code == 404


def test_rules_are_tenant_scoped(client, headers):
    tenant1_before = client.get("/api/rules/active", headers=headers("admin")).json()
    response = client.post(
        "/api/rules",
        headers=headers("other_admin"),
        json={"definition": {"max_income": 5000}, "change_note": "other tenant"},
    )
    assert response.status_code == 201
    tenant1_after = client.get("/api/rules/active", headers=headers("admin")).json()
    assert tenant1_after["version"] == tenant1_before["version"]
    assert tenant1_after["definition"] == tenant1_before["definition"]
    assert client.get("/api/rules/active", headers=headers("other_admin")).json()["version"] == 2


def test_auditor_only_sees_own_tenant_audit(client, headers):
    events = client.get("/api/audit", headers=headers("auditor")).json()
    assert events
    assert all(entry["tenant_id"] == "tenant_relief_dept" for entry in events)
