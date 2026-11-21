"""MOCK payment service (simulates Raast disbursement). Never moves real money."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


def disburse(case_number: str, amount: float, *, approved_by: str) -> dict:
    """Simulate a payment after an officer has approved it."""
    if not approved_by:
        return {
            "status": "blocked",
            "reason": "No officer approval recorded.",
            "mock": True,
            "simulated": True,
        }
    return {
        "transaction_id": "MOCK-RAAST-" + uuid.uuid4().hex[:12].upper(),
        "case_number": case_number,
        "amount": amount,
        "status": "simulated_success",
        "approved_by": approved_by,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "mock": True,
        "simulated": True,
        "notice": "No real money was transferred.",
    }
