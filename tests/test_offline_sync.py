"""Offline-first sync is idempotent and preserves progress."""

from app.models import Case


def _count_cases(db):
    db.expire_all()
    return db.query(Case).count()


def test_offline_operations_sync_once_without_duplicates(client, db, headers):
    before = _count_cases(db)
    operations = [
        {"op_id": "offline-1", "op_type": "scam_report",
         "payload": {"raw_text": "click this link and send OTP relief payment", "district": "Karachi"}},
        {"op_id": "offline-2", "op_type": "voice_intake",
         "payload": {"transcript": "I need relief payment, income 12000"}},
    ]
    first = client.post(
        "/api/sync",
        headers=headers("citizen"),
        json={"client_id": "phone-abc", "operations": operations},
    )
    assert first.status_code == 200, first.text
    assert first.json()["processed"] == 2
    after_first = _count_cases(db)
    assert after_first == before + 2

    second = client.post(
        "/api/sync",
        headers=headers("citizen"),
        json={"client_id": "phone-abc", "operations": operations},
    )
    assert second.json()["duplicates_skipped"] == 2
    assert _count_cases(db) == after_first


def test_sync_status_lists_saved_operations(client, headers):
    client.post(
        "/api/sync",
        headers=headers("citizen"),
        json={
            "client_id": "phone-xyz",
            "operations": [{"op_id": "op-a", "op_type": "scam_report",
                            "payload": {"raw_text": "fake relief message"}}],
        },
    )
    status = client.get("/api/sync/status", headers=headers("citizen"), params={"client_id": "phone-xyz"})
    assert status.status_code == 200
    assert status.json()["operations"][0]["op_id"] == "op-a"


def test_offline_voice_case_is_tagged_with_channel(client, headers):
    result = client.post(
        "/api/sync",
        headers=headers("citizen"),
        json={
            "client_id": "phone-voice",
            "operations": [{"op_id": "v-1", "op_type": "voice_intake",
                            "payload": {"transcript": "relief payment application"}}],
        },
    ).json()
    case_id = result["results"][0]["result"]["case_id"]
    case = client.get(f"/api/cases/{case_id}", headers=headers("citizen")).json()
    assert case["intake_channel"] == "voice"
