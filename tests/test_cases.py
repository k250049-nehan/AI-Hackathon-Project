"""End-to-end relief claim lifecycle, AI decisions and auditability."""

CLAIM = {
    "full_name": "Fatima Bibi",
    "cnic": "12345-1234567-1",
    "category": "widow",
    "monthly_income": 12000,
    "dependents": 3,
    "claim_amount": 10000,
    "district": "Karachi",
}


def _create_claim(client, h, **overrides):
    body = {
        "case_type": "relief_claim",
        "raw_text": (
            "Application for relief payment. I am a widow with 3 dependents. "
            "Monthly income is 12000 rupees. CNIC 12345-1234567-1 Karachi."
        ),
        "claim_data": {**CLAIM, **overrides},
        "intake_channel": "text",
    }
    response = client.post("/api/cases", headers=h, json=body)
    assert response.status_code == 201, response.text
    return response.json()


def test_case_lifecycle_create_assign_review_close(client, headers):
    citizen_h, officer_h = headers("citizen"), headers("officer")
    case = _create_claim(client, citizen_h)
    assert case["case_number"].startswith("RC-")
    assert case["rule_set_id"] is not None
    assert case["decision"] in {"approve", "needs_info", "human_review", "block"}

    assigned = client.post(
        f"/api/cases/{case['id']}/assign",
        headers=officer_h,
        json={"assignee_user_id": "user_officer_imran"},
    )
    assert assigned.status_code == 200, assigned.text
    assert assigned.json()["status"] == "assigned"

    reviewed = client.post(
        f"/api/cases/{case['id']}/review",
        headers=officer_h,
        json={"decision": "approved", "note": "Checked mock documents."},
    )
    assert reviewed.status_code == 200, reviewed.text
    body = reviewed.json()
    assert body["officer_decision"] == "approved"
    assert body["status"] == "approved"
    assert body["payment_mock"]["status"] == "simulated_success"
    assert body["payment_mock"]["mock"] is True

    closed = client.post(f"/api/cases/{case['id']}/close", headers=officer_h)
    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"


def test_scam_report_is_blocked_with_explanation(client, headers):
    h = headers("citizen")
    response = client.post(
        "/api/cases",
        headers=h,
        json={
            "case_type": "scam_report",
            "raw_text": "Congratulations! Relief payment ready. Click https://bit.ly/x and send your OTP urgently.",
            "district": "Karachi",
        },
    )
    assert response.status_code == 201
    case = response.json()
    assert case["jev_label"] == "scam"
    assert case["decision"] == "block"
    assert case["status"] == "blocked"
    assert case["decision_reason_simple"]


def test_two_view_explanation(client, headers):
    h = headers("citizen")
    case_id = client.get("/api/cases", headers=h).json()[0]["id"]
    response = client.get(f"/api/cases/{case_id}/explain", headers=h)
    assert response.status_code == 200
    body = response.json()
    assert body["simple"]
    assert body["simple_urdu"]
    trace = body["audit_trace"]
    assert trace["rule_version"] == 1
    assert trace["model_versions"]["rules"] == "rule-set-v1"
    assert "input_hash" in trace


def test_documents_and_vision_checks(client, headers):
    h = headers("citizen")
    case_id = client.get("/api/cases", headers=h).json()[0]["id"]
    response = client.post(
        f"/api/cases/{case_id}/documents",
        headers=h,
        json={
            "owner_user_id": "user_citizen_fatima",
            "doc_type": "cnic",
            "ocr_text": "Fatima Bibi 12345-1234567-1",
            "qr_valid": True,
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["is_mock"] is True

    suspicious = client.post(
        "/api/ai/vision/analyze",
        headers=h,
        json={
            "ocr_text": "SPECIMEN edited CNIC 12345-1234567-1",
            "qr_valid": False,
            "expected_cnic": "1234512345671",
        },
    )
    assert suspicious.json()["suspicious"] is True
    assert suspicious.json()["route"] == "human_review"


def test_agent_calls_tools_and_requires_human_approval(client, headers):
    case_id = client.get("/api/cases", headers=headers("officer")).json()[0]["id"]
    response = client.post(
        f"/api/cases/{case_id}/agent/run", headers=headers("officer")
    )
    assert response.status_code == 200, response.text
    body = response.json()
    tools = [step["tool"] for step in body["steps"]]
    assert "jev.classify" in tools
    assert "mock_identity.verify" in tools
    assert "rules.evaluate" in tools
    assert "guardrails.check" in tools
    assert body["human_approval_required"] is True
    assert all(step["mock"] is True for step in body["steps"])


def test_audit_records_user_ai_and_agent_actions(client, headers):
    h = headers("officer")
    case_id = client.get("/api/cases", headers=h).json()[0]["id"]
    client.post(f"/api/cases/{case_id}/agent/run", headers=h)
    audit = client.get("/api/audit", headers=h).json()
    actions = {entry["action"] for entry in audit}
    assert "auth.login" in actions
    assert "case.created" in actions
    assert "ai.decision" in actions
    assert "agent.tool.jev.classify" in actions

    ai_decisions = client.get("/api/audit/ai-decisions", headers=h).json()
    assert ai_decisions
    assert "trace" in ai_decisions[0]


def test_dashboard_status_and_history(client, headers):
    h = headers("citizen")
    response = client.get("/api/dashboard", headers=h)
    assert response.status_code == 200
    body = response.json()
    assert body["total_cases"] >= 1
    assert sum(body["by_status"].values()) == body["total_cases"]
    assert len(body["recent_cases"]) >= 1
