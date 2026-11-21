"""Consent visibility, sharing, correction and enforced take-back."""

SUBJECT = "user_citizen_fatima"
HELPER = "user_helper_sana"


def test_citizen_can_see_who_has_their_data(client, headers):
    response = client.get("/api/consent/mine", headers=headers("citizen"))
    assert response.status_code == 200
    shared = response.json()["shared_with"]
    assert any(row["grantee_user_id"] == HELPER for row in shared)
    assert any(row["purpose"] == "department_review" for row in shared)


def test_helper_can_act_only_while_consent_is_active(client, headers):
    helper_h = headers("helper")
    body = {"subject_user_id": SUBJECT, "raw_text": "Please file my relief claim."}
    assert client.post("/api/cases", headers=helper_h, json=body).status_code == 201

    withdrawn = client.post(
        "/api/consent/withdraw",
        headers=headers("citizen"),
        json={
            "subject_user_id": SUBJECT,
            "purpose": "relief_claim_assist",
            "grantee_user_id": HELPER,
            "action": "withdraw",
        },
    )
    assert withdrawn.status_code == 200
    assert withdrawn.json()["withdrawn_records"] >= 1

    denied = client.post("/api/cases", headers=helper_h, json=body)
    assert denied.status_code == 403
    assert denied.json()["error"] in {"consent_required", "consent_withdrawn_or_missing"}


def test_withdrawal_blocks_direct_case_read_and_is_audited(client, headers):
    citizen_h, helper_h = headers("citizen"), headers("helper")
    created = client.post(
        "/api/cases",
        headers=helper_h,
        json={"subject_user_id": SUBJECT, "raw_text": "relief claim for Fatima"},
    ).json()
    case_id = created["id"]

    client.post(
        "/api/consent/withdraw",
        headers=citizen_h,
        json={
            "subject_user_id": SUBJECT,
            "purpose": "relief_claim_assist",
            "grantee_user_id": HELPER,
            "action": "withdraw",
        },
    )
    response = client.get(f"/api/cases/{case_id}", headers=helper_h)
    assert response.status_code == 403

    events = client.get("/api/audit/consent-events", headers=headers("auditor")).json()
    withdrawals = [event for event in events if event["action"] == "consent.withdrawn"]
    assert withdrawals
    assert withdrawals[0]["detail"]["access_blocked"] is True


def test_access_check_endpoint_reflects_withdrawal(client, headers):
    check_url = "/api/consent/check?subject_user_id=%s&purpose=relief_claim_assist&scope=submit_claim" % SUBJECT
    assert client.get(check_url, headers=headers("helper")).json()["allowed"] is True
    client.post(
        "/api/consent/withdraw",
        headers=headers("citizen"),
        json={"subject_user_id": SUBJECT, "purpose": "relief_claim_assist", "grantee_user_id": HELPER},
    )
    assert client.get(check_url, headers=headers("helper")).json()["allowed"] is False


def test_regrant_restores_access(client, headers):
    client.post(
        "/api/consent/withdraw",
        headers=headers("citizen"),
        json={"subject_user_id": SUBJECT, "purpose": "relief_claim_assist", "grantee_user_id": HELPER},
    )
    granted = client.post(
        "/api/consent/grant",
        headers=headers("citizen"),
        json={
            "subject_user_id": SUBJECT,
            "grantee_user_id": HELPER,
            "purpose": "relief_claim_assist",
            "scopes": ["read_profile", "read_claim", "submit_claim"],
        },
    )
    assert granted.status_code == 201
    assert granted.json()["status"] == "active"
    response = client.post(
        "/api/cases",
        headers=headers("helper"),
        json={"subject_user_id": SUBJECT, "raw_text": "relief claim again"},
    )
    assert response.status_code == 201


def test_data_correction_is_audited(client, headers):
    response = client.post(
        "/api/consent/correct",
        headers=headers("citizen"),
        json={"full_name": "Fatima Bibi Khan", "phone": "03001112223"},
    )
    assert response.status_code == 200
    assert client.get("/api/auth/me", headers=headers("citizen")).json()["phone"] == "03001112223"
    events = client.get("/api/audit", headers=headers("auditor"), params={"action": "consent.data_corrected"}).json()
    assert events
    assert "before" in events[0]["detail"]
