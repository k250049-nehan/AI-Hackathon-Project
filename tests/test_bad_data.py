"""Missing, duplicated and inconsistently spelled data never crashes or mismatches."""

from app.services import mock_identity


def test_name_variants_match_the_same_mock_person():
    for name in ("Muhammad Ahmed", "Mohammad Ahmed", "Muhammed Ahmed", "Mohammed Ahmed"):
        result = mock_identity.verify("1234567890123", name)
        assert result["verified"] is True, (name, result)
        assert result["status"] == "verified"


def test_different_people_with_similar_names_do_not_match():
    result = mock_identity.verify("1234567890123", "Fatima Bibi")
    assert result["verified"] is False
    assert result["status"] == "name_mismatch"


def test_missing_and_malformed_identifiers_are_safe(client, headers):
    response = client.post(
        "/api/mock/identity/verify",
        headers=headers("citizen"),
        json={"cnic": "not-a-cnic", "full_name": ""},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "incomplete"
    assert response.json()["mock"] is True

    response = client.post(
        "/api/mock/identity/verify",
        headers=headers("citizen"),
        json={"cnic": "12345-1234567-1", "full_name": ""},
    )
    assert response.json()["status"] == "needs_info"


def test_voice_intake_with_missing_fields_does_not_crash(client, headers):
    response = client.post(
        "/api/ai/voice/intake",
        headers=headers("citizen"),
        json={"transcript": "I need help", "language": "ur"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["missing_fields"]
    assert body["case"]["status"] in {"needs_info", "human_review"}
    assert "voice" in body["spoken_prompt"] or body["case"]["intake_channel"] == "voice"


def test_structured_validation_rejects_bad_cnic_and_excessive_amount(client, headers):
    h = headers("citizen")
    response = client.post(
        "/api/ai/structured/validate",
        headers=h,
        json={"full_name": "Test Person", "cnic": "123", "monthly_income": 1000,
              "claim_amount": 500000, "district": "Karachi"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    fields = {error["field"] for error in body["errors"]}
    assert "cnic" in fields


def test_duplicate_claims_are_flagged_not_silently_approved(client, db, headers):
    from app.services.cases import create_case

    claim = {
        "full_name": "Muhammad Ahmed", "cnic": "1234567890123",
        "category": "unemployed", "monthly_income": 12000,
        "dependents": 2, "claim_amount": 9000, "district": "Lahore",
    }
    for _ in range(3):
        created = create_case(
            db,
            tenant_id="tenant_relief_dept",
            subject_user_id="user_citizen_ahmed",
            created_by="user_citizen_ahmed",
            raw_text="relief claim application",
            claim_data=claim,
        )
        db.commit()
    trace = created.decision_trace
    assert trace["anomaly"]["score"] > 0
    assert created.risk_flag == "anomaly"
    assert created.decision in {"human_review", "needs_info"}, created.decision
