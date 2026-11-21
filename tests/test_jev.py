"""Jev-style confidence routing and honest false-alarm reporting."""

SCAM_TEXT = (
    "Congratulations! Your relief payment of Rs. 25000 is ready. "
    "Click here https://bit.ly/claimnow and send your CNIC and OTP urgently."
)
LEGIT_TEXT = (
    "Application for relief payment. I am a widow with 3 dependents. "
    "Monthly income is 12000 rupees and my CNIC is 12345-1234567-1 in Karachi."
)


def test_scam_with_multiple_signals_is_blocked(client, headers):
    result = client.post("/api/ai/classify", headers=headers("citizen"), json={"text": SCAM_TEXT}).json()
    assert result["label"] == "scam"
    assert result["confidence"] >= 0.85
    assert result["route"] == "auto_block"
    assert result["model_version"].startswith("jev-")


def test_legitimate_claim_is_not_a_false_alarm(client, headers):
    result = client.post("/api/ai/classify", headers=headers("citizen"), json={"text": LEGIT_TEXT}).json()
    assert result["label"] != "scam"
    assert result["route"] != "auto_block"


def test_single_weak_signal_is_handed_to_human(client, headers):
    result = client.post(
        "/api/ai/classify", headers=headers("citizen"), json={"text": "Relief payment"}
    ).json()
    assert result["route"] == "human_handoff"
    assert result["confidence"] < 0.65


def test_complaint_and_request_are_routed(client, headers):
    h = headers("citizen")
    complaint = client.post(
        "/api/ai/classify", headers=h, json={"text": "This is a complaint, my payment never arrived."}
    ).json()
    assert complaint["label"] == "complaint"
    assert complaint["route"] != "human_handoff"


def test_rag_answers_with_sources(client, headers):
    response = client.post(
        "/api/ai/rag", headers=headers("citizen"), json={"question": "What is the income limit?", "top_k": 2}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sources"]
    assert "Source:" in body["answer"]
    assert body["simulated"] is True


def test_unknown_rag_question_admits_uncertainty(client, headers):
    body = client.post(
        "/api/ai/rag", headers=headers("citizen"), json={"question": "zzzz qqqq xxxx"}
    ).json()
    assert body["sources"] == []
    assert "not sure" in body["answer"]


def test_evaluation_dashboard_reports_false_alarms_honestly(client, headers):
    summary = client.get("/api/evaluation/summary", headers=headers("admin")).json()
    assert summary["total_evaluations"] >= 12
    assert summary["false_alarms"] == 1
    assert summary["missed_scams"] == 1
    assert summary["false_alarm_rate"] > 0
    assert summary["cost_model"]["ratio"] == 10.0
    assert summary["avg_latency_ms"] > 0
