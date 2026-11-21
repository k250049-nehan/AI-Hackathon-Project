"""Deterministic, fully mocked seed data for the live demo and tests."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Consent, EvaluationRecord, Tenant, User
from app.rules.engine import DEFAULT_DEFINITION, create_ruleset
from app.security import hash_password
from app.services.cases import create_case

TENANT_ID = "tenant_relief_dept"
TENANT2_ID = "tenant_district_north"

IDS = {
    "citizen_fatima": "user_citizen_fatima",
    "citizen_ahmed": "user_citizen_ahmed",
    "helper": "user_helper_sana",
    "officer": "user_officer_imran",
    "admin": "user_admin_nadia",
    "auditor": "user_auditor_usman",
    "citizen2": "user_citizen_zainab",
    "helper2": "user_helper_bilal",
    "officer2": "user_officer_hina",
    "admin2": "user_admin_other",
    "auditor2": "user_auditor_other",
}

PASSWORD = "Demo@123"


def seed_database(db: Session) -> None:
    """Seed once. Safe to call on every startup."""
    if db.get(Tenant, TENANT_ID):
        return

    tenants = [
        Tenant(id=TENANT_ID, name="Mock Relief Department", slug="relief-dept", plan="team", is_active=True),
        Tenant(id=TENANT2_ID, name="Mock District North", slug="district-north", plan="free", is_active=True),
    ]
    db.add_all(tenants)
    db.flush()

    def user(key: str, tenant: str, email: str, name: str, role: str, language: str = "ur") -> User:
        record = User(
            id=IDS[key],
            tenant_id=tenant,
            email=email,
            full_name=name,
            password_hash=hash_password(PASSWORD),
            role=role,
            phone="03000000000",
            preferred_language=language,
            is_active=True,
        )
        db.add(record)
        return record

    user("citizen_fatima", TENANT_ID, "fatima@mock.local", "Fatima Bibi", "citizen")
    user("citizen_ahmed", TENANT_ID, "ahmed@mock.local", "Muhammad Ahmed", "citizen", "en")
    user("helper", TENANT_ID, "helper@mock.local", "Sana Helper", "helper")
    user("officer", TENANT_ID, "officer@mock.local", "Imran Officer", "officer", "en")
    user("admin", TENANT_ID, "admin@mock.local", "Nadia Admin", "admin", "en")
    user("auditor", TENANT_ID, "auditor@mock.local", "Usman Auditor", "auditor", "en")

    user("citizen2", TENANT2_ID, "zainab@mock.local", "Zainab Bibi", "citizen")
    user("helper2", TENANT2_ID, "helper2@mock.local", "Bilal Helper", "helper")
    user("officer2", TENANT2_ID, "officer2@mock.local", "Hina Officer", "officer")
    user("admin2", TENANT2_ID, "admin2@mock.local", "Admin Two", "admin")
    user("auditor2", TENANT2_ID, "auditor2@mock.local", "Auditor Two", "auditor")

    db.flush()

    consents = [
        Consent(
            tenant_id=TENANT_ID,
            subject_user_id=IDS["citizen_fatima"],
            grantee_user_id=IDS["helper"],
            grantee_role=None,
            purpose="relief_claim_assist",
            scopes=["read_profile", "read_claim", "submit_claim", "manage_consent"],
            status="active",
        ),
        Consent(
            tenant_id=TENANT_ID,
            subject_user_id=IDS["citizen_fatima"],
            grantee_user_id=None,
            grantee_role="officer",
            purpose="department_review",
            scopes=["read_claim", "review_claim"],
            status="active",
        ),
        Consent(
            tenant_id=TENANT_ID,
            subject_user_id=IDS["citizen_fatima"],
            grantee_user_id=None,
            grantee_role="admin",
            purpose="department_review",
            scopes=["read_claim", "review_claim"],
            status="active",
        ),
        Consent(
            tenant_id=TENANT_ID,
            subject_user_id=IDS["citizen_ahmed"],
            grantee_user_id=IDS["helper"],
            grantee_role=None,
            purpose="relief_claim_assist",
            scopes=["read_profile", "read_claim", "submit_claim", "manage_consent"],
            status="active",
        ),
        Consent(
            tenant_id=TENANT_ID,
            subject_user_id=IDS["citizen_ahmed"],
            grantee_user_id=None,
            grantee_role="officer",
            purpose="department_review",
            scopes=["read_claim", "review_claim"],
            status="active",
        ),
        Consent(
            tenant_id=TENANT_ID,
            subject_user_id=IDS["citizen_ahmed"],
            grantee_user_id=None,
            grantee_role="admin",
            purpose="department_review",
            scopes=["read_claim", "review_claim"],
            status="active",
        ),
        Consent(
            tenant_id=TENANT2_ID,
            subject_user_id=IDS["citizen2"],
            grantee_user_id=IDS["helper2"],
            purpose="relief_claim_assist",
            scopes=["read_profile", "read_claim", "submit_claim", "manage_consent"],
            status="active",
        ),
        Consent(
            tenant_id=TENANT2_ID,
            subject_user_id=IDS["citizen2"],
            grantee_user_id=None,
            grantee_role="officer",
            purpose="department_review",
            scopes=["read_claim", "review_claim"],
            status="active",
        ),
    ]
    db.add_all(consents)

    create_ruleset(
        db,
        tenant_id=TENANT_ID,
        definition=dict(DEFAULT_DEFINITION),
        change_note="Initial mock eligibility rules.",
        created_by=IDS["admin"],
    )
    create_ruleset(
        db,
        tenant_id=TENANT2_ID,
        definition=dict(DEFAULT_DEFINITION),
        change_note="Initial mock eligibility rules.",
        created_by=IDS["admin2"],
    )

    evaluation_rows = [
        ("scam", "scam", 0.97, 11.2),
        ("scam", "scam", 0.93, 12.8),
        ("scam", "scam", 0.91, 10.4),
        ("scam", "scam", 0.88, 13.1),
        ("relief_claim", "relief_claim", 0.86, 9.7),
        ("relief_claim", "relief_claim", 0.84, 10.9),
        ("relief_claim", "relief_claim", 0.89, 8.6),
        ("complaint", "complaint", 0.80, 12.2),
        ("scam", "relief_claim", 0.72, 14.0),   # honest false alarm
        ("relief_claim", "scam", 0.60, 15.3),   # honest missed scam
        ("unknown", "unknown", 0.31, 9.1),
        ("unknown", "unknown", 0.42, 10.0),
    ]
    for predicted, actual, confidence, latency in evaluation_rows:
        db.add(
            EvaluationRecord(
                tenant_id=TENANT_ID,
                case_id=None,
                predicted_label=predicted,
                actual_label=actual,
                confidence=confidence,
                latency_ms=latency,
                was_false_alarm=predicted == "scam" and actual != "scam",
                was_missed=actual == "scam" and predicted != "scam",
                notes="Seeded mock evaluation sample.",
            )
        )

    db.flush()

    # Two demo cases give the dashboard and review queue something to show.
    create_case(
        db,
        tenant_id=TENANT_ID,
        subject_user_id=IDS["citizen_fatima"],
        created_by=IDS["citizen_fatima"],
        case_type="relief_claim",
        raw_text=(
            "Application for relief payment. I am a widow with 3 dependents. "
            "Monthly income is 12000 rupees and I live in Karachi. "
            "CNIC 12345-1234567-1. Please check my benefit claim."
        ),
        claim_data={
            "full_name": "Fatima Bibi",
            "cnic": "1234512345671",
            "category": "widow",
            "monthly_income": 12000,
            "dependents": 3,
            "claim_amount": 10000,
            "district": "Karachi",
        },
        intake_channel="voice",
        district="Karachi",
    )
    create_case(
        db,
        tenant_id=TENANT_ID,
        subject_user_id=IDS["citizen_ahmed"],
        created_by=IDS["citizen_ahmed"],
        case_type="scam_report",
        raw_text=(
            "Congratulations! Your relief payment of Rs. 25000 is ready. "
            "Click here https://bit.ly/claim-now to confirm your CNIC and OTP urgently."
        ),
        intake_channel="text",
        district="Lahore",
    )
    db.commit()
