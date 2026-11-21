"""Versioned rule changes, no-redeploy behaviour and Digital Twin replay."""

CLAIM = {
    "full_name": "Muhammad Ahmed",
    "cnic": "12345-1234567-1",
    "category": "unemployed",
    "monthly_income": 12000,
    "dependents": 2,
    "claim_amount": 9000,
    "district": "Lahore",
}


def _make_case(client, h):
    response = client.post(
        "/api/cases",
        headers=h,
        json={
            "raw_text": "Application for relief payment, monthly income 12000, unemployed, Lahore.",
            "claim_data": CLAIM,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_rule_change_applies_immediately_without_redeploy(client, headers):
    citizen_h, admin_h = headers("citizen"), headers("admin")
    before = _make_case(client, citizen_h)
    old_id = before["rule_set_id"]
    old_version = client.get("/api/rules/active", headers=admin_h).json()["version"]

    published = client.post(
        "/api/rules",
        headers=admin_h,
        json={
            "definition": {
                "max_income": 8000,
                "max_claim_amount": 5000,
                "auto_approve_min_confidence": 0.99,
                "note": "tighter rule",
            },
            "change_note": "Tightened income limit for fraud review.",
        },
    )
    assert published.status_code == 201, published.text
    new_rule = published.json()
    assert new_rule["version"] == old_version + 1
    assert new_rule["is_active"] is True

    active = client.get("/api/rules/active", headers=admin_h).json()
    assert active["version"] == old_version + 1
    assert active["definition"]["max_income"] == 8000

    after = _make_case(client, citizen_h)
    assert after["rule_set_id"] == new_rule["id"]
    assert after["rule_set_id"] != old_id
    assert after["decision_trace"]["rule_version"] == new_rule["version"]

    unchanged = client.get(f"/api/cases/{before['id']}", headers=citizen_h).json()
    assert unchanged["rule_set_id"] == old_id
    assert unchanged["decision_trace"]["rule_version"] == old_version


def test_rule_publication_is_audited(client, headers):
    response = client.post(
        "/api/rules",
        headers=headers("admin"),
        json={"definition": {"max_income": 15000}, "change_note": "audited change"},
    )
    assert response.status_code == 201
    events = client.get(
        "/api/audit", headers=headers("auditor"), params={"action": "rule.published"}
    ).json()
    assert events
    assert events[0]["detail"]["change_note"] == "audited change"


def test_digital_twin_does_not_change_live_rules(client, headers):
    admin_h = headers("admin")
    live_before = client.get("/api/rules/active", headers=admin_h).json()
    response = client.post(
        "/api/rules/digital-twin/simulate",
        headers=admin_h,
        json={
            "definition": {"max_income": 8000, "max_claim_amount": 5000},
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["cases_simulated"] >= 2
    assert body["live_rules_unchanged"] is True
    assert "decisions_changed" in body
    live_after = client.get("/api/rules/active", headers=admin_h).json()
    assert live_after["version"] == live_before["version"]
    assert live_after["definition"] == live_before["definition"]
