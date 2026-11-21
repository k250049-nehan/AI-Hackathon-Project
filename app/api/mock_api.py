"""Clean APIs over the mock identity, payment and data services."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.errors import AppError
from app.security import get_current_user, require_roles
from app.services import mock_data, mock_identity, mock_payment

router = APIRouter(prefix="/api/mock", tags=["mock-services"])


class VerifyRequest(BaseModel):
    cnic: str
    full_name: str | None = None


class PaymentRequest(BaseModel):
    case_number: str
    amount: float
    approved_by: str


@router.post("/identity/verify", summary="MOCK identity verification")
def verify_identity(
    payload: VerifyRequest,
    actor=Depends(get_current_user),
) -> dict:
    return mock_identity.verify(payload.cnic, payload.full_name)


@router.get("/data/{cnic}", summary="MOCK consented data lookup")
def lookup_data(cnic: str, actor=Depends(get_current_user)) -> dict:
    return mock_data.get_record(cnic)


@router.post("/payment/disburse", summary="MOCK payment disbursement (officer only)")
def disburse(
    payload: PaymentRequest,
    actor=Depends(require_roles("officer", "admin")),
) -> dict:
    if not payload.approved_by:
        raise AppError(422, "approval_required", "An officer id is required.")
    return mock_payment.disburse(
        payload.case_number,
        payload.amount,
        approved_by=payload.approved_by or actor.id,
    )


@router.get("/families", summary="MOCK helper-mode family directory")
def families(actor=Depends(get_current_user)) -> dict:
    return {"families": mock_data.list_mock_families(), "mock": True}
