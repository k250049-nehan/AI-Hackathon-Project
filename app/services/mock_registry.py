"""Mock citizen registry. Every record below is fabricated for the prototype."""

from __future__ import annotations

MOCK_CITIZENS: list[dict] = [
    {
        "cnic": "1234512345671",
        "full_name": "Fatima Bibi",
        "district": "Karachi",
        "category": "widow",
        "monthly_income": 12000,
        "dependents": 3,
        "phone": "03001234567",
        "record_complete": True,
    },
    {
        "cnic": "1234567890123",
        "full_name": "Muhammad Ahmed",
        "district": "Lahore",
        "category": "unemployed",
        "monthly_income": 18000,
        "dependents": 2,
        "phone": "03009876543",
        "record_complete": True,
    },
    {
        "cnic": "1111122222333",
        "full_name": "Aisha Khatoon",
        "district": "Hyderabad",
        "category": "low_income",
        "monthly_income": 9000,
        "dependents": 4,
        "phone": None,
        "record_complete": False,
        "missing_fields": ["phone", "income_proof"],
    },
    {
        # Deliberate near-duplicate used to exercise fuzzy matching / anomaly checks.
        "cnic": "4444455555666",
        "full_name": "Mohammad Ahmed",
        "district": "Lahore",
        "category": "low_income",
        "monthly_income": 21000,
        "dependents": 1,
        "phone": "03001112223",
        "record_complete": True,
    },
]

MOCK_HELPER_FAMILIES: list[dict] = [
    {"family_id": f"F{index:02d}", "subject_name": f"Mock Family Member {index}"}
    for index in range(1, 41)
]
