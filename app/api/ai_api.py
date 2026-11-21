"""Public-facing AI capabilities, all local and explicitly simulated."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai import anomaly as anomaly_module
from app.ai import jev as jev_module
from app.ai import rag as rag_module
from app.ai import structured as structured_module
from app.ai import vision as vision_module
from app.ai.explain import explain
from app.db import get_db
from app.errors import AppError
from app.models import User
from app.rules.engine import get_active_ruleset
from app.schemas import (
    CaseOut,
    ExplainOut,
    JevOut,
    JevRequest,
    RAGRequest,
    RagOut,
    VoiceIntakeRequest,
)
from app.security import enforce_consent, get_current_user
from app.services.cases import create_case

from app.api.helpers import enforce_usage_limit

router = APIRouter(prefix="/api/ai", tags=["ai"])


class TextRequest(BaseModel):
    text: str


class AnomalyRequest(BaseModel):
    claim: dict
    past_claims: list[dict] = []


class VisionRequest(BaseModel):
    ocr_text: str | None = None
    qr_valid: bool | None = None
    blurry: bool = False
    expected_cnic: str | None = None


class ExtractOut(BaseModel):
    extracted: dict
    missing_fields: list[str]
    complete: bool
    model_version: str
    simulated: bool = True


class ValidateOut(BaseModel):
    valid: bool
    data: dict
    errors: list[dict]
    model_version: str


@router.post("/classify", response_model=JevOut, summary="Jev-style classify, score and route")
def classify_text(payload: JevRequest, actor: User = Depends(get_current_user)) -> JevOut:
    ruleset = get_active_ruleset_by_tenant(actor)
    result = jev_module.classify(
        payload.text,
        {
            "auto_approve_min_confidence": ruleset.definition["auto_approve_min_confidence"],
            "ask_info_min_confidence": ruleset.definition["ask_info_min_confidence"],
            "scam_block_confidence": ruleset.definition["scam_block_confidence"],
        },
    )
    return JevOut(**result)


def get_active_ruleset_by_tenant(actor: User):
    from app.db import SessionLocal
    from app.rules.engine import get_active_ruleset as fetch

    with SessionLocal() as session:
        return fetch(session, actor.tenant_id)


@router.post("/rag", response_model=RagOut, summary="Answer from mock official rules with sources")
def rag_answer(payload: RAGRequest, actor: User = Depends(get_current_user)) -> RagOut:
    result = rag_module.answer(payload.question, payload.top_k)
    return RagOut(**result)


@router.post("/explain-text", response_model=ExplainOut, summary="Explain any decision in two views")
def explain_text(payload: dict, actor: User = Depends(get_current_user)) -> ExplainOut:
    decision = str(payload.get("decision", "human_review"))
    result = explain(
        decision,
        payload.get("reasons", []),
        payload.get("trace", {}),
        float(payload.get("confidence", 0.0)),
        rule_version=payload.get("rule_version"),
    )
    return ExplainOut(**result)


@router.post("/structured/extract", response_model=ExtractOut, summary="Extract form fields from messy text")
def extract_fields(payload: TextRequest, actor: User = Depends(get_current_user)) -> ExtractOut:
    return ExtractOut(**structured_module.extract_claim_from_text(payload.text))


@router.post("/structured/validate", response_model=ValidateOut, summary="Validate a structured claim")
def validate_fields(payload: dict, actor: User = Depends(get_current_user)) -> ValidateOut:
    return ValidateOut(**structured_module.validate_claim(payload))


@router.post("/anomaly", summary="Detect duplicate or unusual claims")
def detect_anomaly(payload: AnomalyRequest, actor: User = Depends(get_current_user)) -> dict:
    return anomaly_module.detect_anomaly(payload.claim, payload.past_claims)


@router.post("/vision/analyze", summary="Mock OCR / QR / forgery analysis")
def analyze_document(payload: VisionRequest, actor: User = Depends(get_current_user)) -> dict:
    return vision_module.analyze(
        payload.ocr_text,
        qr_valid=payload.qr_valid,
        blurry=payload.blurry,
        expected_cnic=payload.expected_cnic,
    )


@router.post("/voice/intake", response_model=dict, summary="Voice-first intake for low-literacy citizens")
def voice_intake(
    payload: VoiceIntakeRequest,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> dict:
    subject = payload.subject_user_id or actor.id
    if subject != actor.id:
        enforce_consent(db, actor, subject, "relief_claim_assist", "submit_claim")
    prepared = structured_module.prepare_voice_claim(payload.transcript, payload.claim_data)
    if prepared["errors"]:
        raise AppError(
            422,
            "invalid_claim",
            "Structured claim failed validation.",
            {"errors": prepared["errors"]},
        )
    claim = dict(prepared["claim"])

    enforce_usage_limit(db, actor.tenant_id)
    case = create_case(
        db,
        tenant_id=actor.tenant_id,
        subject_user_id=subject,
        created_by=actor.id,
        case_type="relief_claim",
        raw_text=payload.transcript,
        claim_data=claim,
        intake_channel="voice",
        district=claim.get("district"),
    )
    db.commit()
    prompt = (
        "We saved your voice request. We still need: "
        + ", ".join(prepared["missing_fields"])
        + ". Please answer by voice."
        if prepared["missing_fields"]
        else "We saved your voice request. A human will check it before any payment."
    )
    return {
        "case": CaseOut.model_validate(case),
        "extracted": prepared["extracted"],
        "missing_fields": prepared["missing_fields"],
        "spoken_prompt": prompt,
        "language": payload.language,
        "audio_transcribed_by": payload.audio_transcribed_by,
        "simulated": True,
    }
