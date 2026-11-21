"""Labelled claim fields feed the same intake and offline decision paths."""

FULL_CLAIM = {
    "full_name": "Muhammad Ahmed",
    "cnic": "12345-6789012-3",
    "district": "Lahore",
    "category": "unemployed",
    "monthly_income": 18000,
    "claim_amount": 5000,
    "dependents": 2,
}


def test_voice_intake_uses_labelled_fields_over_guessed_values(client, headers):
    response = client.post(
        "/api/ai/voice/intake",
        headers=headers("citizen"),
        json={"transcript": "I need help", "language": "en", "claim_data": FULL_CLAIM},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["missing_fields"] == []
    assert body["extracted"]["cnic"] == "1234567890123"
    assert body["extracted"]["district"] == "Lahore"
    assert body["case"]["claim_data"]["cnic"] == "1234567890123"
    assert body["case"]["decision_trace"]["checks"]


def test_voice_intake_rejects_invalid_labelled_fields(client, headers):
    bad_claim = {**FULL_CLAIM, "cnic": "123"}
    response = client.post(
        "/api/ai/voice/intake",
        headers=headers("citizen"),
        json={"transcript": "I need help", "language": "en", "claim_data": bad_claim},
    )
    assert response.status_code == 422, response.text
    body = response.json()
    assert body["error"] == "invalid_claim"
    assert "cnic" in {error["field"] for error in body["details"]["errors"]}


def test_offline_sync_replays_labelled_claim_data(client, headers):
    response = client.post(
        "/api/sync",
        headers=headers("citizen"),
        json={
            "client_id": "structured-ui",
            "operations": [
                {
                    "op_id": "structured-claim-1",
                    "op_type": "voice_intake",
                    "payload": {"transcript": "I need help", "claim_data": FULL_CLAIM},
                }
            ],
        },
    )
    assert response.status_code == 200, response.text
    result = response.json()["results"][0]["result"]
    assert "case_number" in result
    cases = client.get("/api/cases", headers=headers("citizen")).json()
    case = next(item for item in cases if item["case_number"] == result["case_number"])
    assert case["claim_data"]["cnic"] == "1234567890123"
    assert case["claim_data"]["district"] == "Lahore"


def test_intake_has_separate_labelled_fields(client):
    html = client.get("/").text
    for element_id in (
        "claimFullName", "claimCnic", "claimDistrict", "claimCategory",
        "claimIncome", "claimAmount", "claimDependents", "textInput",
    ):
        assert 'id="%s"' % element_id in html
    assert 'data-i18n="claimDetailsTitle"' in html
    assert 'data-i18n="requestLabel"' in html
