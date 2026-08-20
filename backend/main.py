from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from analysis import analyze_evidence
from database import Base, engine, get_db
from extraction import prepare_claim
from models import Claim, Verification
from schemas import (
    ArticleVerificationRequest,
    ArticleVerificationResponse,
    ClaimVerificationRequest,
    EvidenceResponse,
    HealthResponse,
    VerificationResponse,
)
from sources import EvidenceService
from usage import can_verify, record_verification
from verification import verify_claim


app = FastAPI(
    title="Verify News API",
    description="Evidence-based news and claim verification API.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)

evidence_service = EvidenceService()


def get_user_identifier() -> str:
    """
    Temporary anonymous identifier for the local prototype.

    Authentication will be introduced later if required.
    """
    return "anonymous"


def build_evidence_response(evidence) -> list[EvidenceResponse]:
    return [
        EvidenceResponse(
            source_name=item.publisher,
            source_type=item.source_type,
            source_url=item.url,
            publication_date=item.publication_date,
            evidence_text=item.evidence_text,
            relationship=item.relationship,
        )
        for item in evidence
    ]


def store_verification(
    db: Session,
    prepared_claim: dict,
    result,
) -> Verification:
    claim = Claim(
        original_text=prepared_claim["original_text"],
        normalized_text=prepared_claim["normalized_text"],
        subject=prepared_claim["subject"],
        event=prepared_claim["event"],
        location=prepared_claim["location"],
        claim_date=prepared_claim["claim_date"],
    )

    db.add(claim)
    db.flush()

    verification = Verification(
        claim_id=claim.id,
        verdict=result.verdict,
        confidence=result.confidence,
        explanation=result.explanation,
    )

    db.add(verification)
    db.commit()
    db.refresh(verification)

    return verification


@app.get(
    "/api/health",
    response_model=HealthResponse,
)
def health_check():
    return HealthResponse(
        status="ok",
        service="verify-news-api",
    )


@app.post(
    "/api/verify/claim",
    response_model=VerificationResponse,
)
def verify_claim_endpoint(
    request: ClaimVerificationRequest,
    db: Session = Depends(get_db),
):
    user_identifier = get_user_identifier()

    if not can_verify(db, user_identifier):
        raise HTTPException(
            status_code=429,
            detail=(
                "The free daily verification limit has been reached."
            ),
        )

    prepared_claim = prepare_claim(request.claim)

    if not prepared_claim["normalized_text"]:
        raise HTTPException(
            status_code=400,
            detail="A valid claim is required.",
        )

    evidence = evidence_service.search(
        prepared_claim["normalized_text"]
    )

    analysis = analyze_evidence(
        prepared_claim["normalized_text"],
        evidence,
    )

    result = verify_claim(
        prepared_claim["normalized_text"],
        evidence,
    )

    if not result.explanation:
        result.explanation = (
            "The verification result was generated from the "
            "available evidence."
        )

    verification = store_verification(
        db,
        prepared_claim,
        result,
    )

    record_verification(
        db,
        user_identifier,
    )

    return VerificationResponse(
        verification_id=verification.id,
        claim=prepared_claim["original_text"],
        normalized_claim=prepared_claim["normalized_text"],
        verdict=result.verdict,
        confidence=result.confidence,
        explanation=result.explanation,
        evidence=build_evidence_response(result.evidence),
        verified_at=verification.verified_at,
    )


@app.post(
    "/api/verify/article",
    response_model=ArticleVerificationResponse,
)
def verify_article_endpoint(
    request: ArticleVerificationRequest,
    db: Session = Depends(get_db),
):
    if not request.article_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Article text is required.",
        )

    user_identifier = get_user_identifier()

    if not can_verify(db, user_identifier):
        raise HTTPException(
            status_code=429,
            detail=(
                "The free daily verification limit has been reached."
            ),
        )

    prepared_claim = prepare_claim(request.article_text)

    if not prepared_claim["normalized_text"]:
        raise HTTPException(
            status_code=400,
            detail="The article does not contain usable text.",
        )

    evidence = evidence_service.search(
        prepared_claim["normalized_text"]
    )

    result = verify_claim(
        prepared_claim["normalized_text"],
        evidence,
    )

    verification = store_verification(
        db,
        prepared_claim,
        result,
    )

    record_verification(
        db,
        user_identifier,
    )

    article_claim = {
        "claim": prepared_claim["original_text"],
        "verification_id": verification.id,
        "verdict": result.verdict,
        "confidence": result.confidence,
        "explanation": result.explanation,
        "evidence": build_evidence_response(result.evidence),
    }

    return ArticleVerificationResponse(
        title=request.title,
        publisher=request.publisher,
        url=request.url,
        claims=[article_claim],
    )


@app.get(
    "/api/verification/{verification_id}",
    response_model=VerificationResponse,
)
def get_verification(
    verification_id: int,
    db: Session = Depends(get_db),
):
    verification = db.get(
        Verification,
        verification_id,
    )

    if verification is None:
        raise HTTPException(
            status_code=404,
            detail="Verification not found.",
        )

    claim = verification.claim

    evidence = [
        item
        for item in claim.evidence
    ]

    evidence_response = [
        EvidenceResponse(
            source_name=item.source.publisher or item.source.domain or "",
            source_type=item.source.source_type or "Unknown",
            source_url=item.source.url,
            publication_date=item.source.publication_date,
            evidence_text=item.evidence_text,
            relationship=item.relationship,
        )
        for item in evidence
    ]

    return VerificationResponse(
        verification_id=verification.id,
        claim=claim.original_text,
        normalized_claim=claim.normalized_text,
        verdict=verification.verdict,
        confidence=verification.confidence,
        explanation=verification.explanation,
        evidence=evidence_response,
        verified_at=verification.verified_at,
    )
