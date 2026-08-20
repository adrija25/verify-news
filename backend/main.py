from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from extraction import extract_claims, prepare_claim
from models import Claim, Verification
from schemas import (
    ArticleVerificationRequest,
    ArticleVerificationResponse,
    ArticleClaimResult,
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
    """
    Convert internal evidence objects into API response objects.
    """

    return [
        EvidenceResponse(
            source_name=item.publisher or item.domain or "Unknown source",
            source_type=item.source_type or "Unknown",
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
    """
    Store one claim and its verification result.
    """

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


def build_verification_response(
    verification: Verification,
) -> VerificationResponse:
    """
    Build the full verification response for a stored verification.
    """

    claim = verification.claim

    evidence_response = [
        EvidenceResponse(
            source_name=item.source.publisher
            or item.source.domain
            or "Unknown source",
            source_type=item.source.source_type or "Unknown",
            source_url=item.source.url,
            publication_date=item.source.publication_date,
            evidence_text=item.evidence_text,
            relationship=item.relationship,
        )
        for item in claim.evidence
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
    """
    Verify one user-submitted claim.
    """

    user_identifier = get_user_identifier()

    if not can_verify(db, user_identifier):
        raise HTTPException(
            status_code=429,
            detail="The free daily verification limit has been reached.",
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

    return build_verification_response(verification)


@app.post(
    "/api/verify/article",
    response_model=ArticleVerificationResponse,
)
def verify_article_endpoint(
    request: ArticleVerificationRequest,
    db: Session = Depends(get_db),
):
    """
    Extract multiple likely factual claims from an article
    and verify them individually.
    """

    if not request.article_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Article text is required.",
        )

    user_identifier = get_user_identifier()

    if not can_verify(db, user_identifier):
        raise HTTPException(
            status_code=429,
            detail="The free daily verification limit has been reached.",
        )

    claims = extract_claims(
        request.article_text,
        max_claims=5,
    )

    if not claims:
        prepared_claim = prepare_claim(request.article_text)

        if not prepared_claim["normalized_text"]:
            raise HTTPException(
                status_code=400,
                detail="The article does not contain usable text.",
            )

        claims = [prepared_claim]

    article_results = []

    for prepared_claim in claims:
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

        article_results.append(
            ArticleClaimResult(
                claim=prepared_claim["original_text"],
                verification_id=verification.id,
                verdict=result.verdict,
                confidence=result.confidence,
                explanation=result.explanation,
                evidence=build_evidence_response(
                    result.evidence
                ),
            )
        )

    record_verification(
        db,
        user_identifier,
    )

    return ArticleVerificationResponse(
        title=request.title,
        publisher=request.publisher,
        url=request.url,
        claims=article_results,
    )


@app.get(
    "/api/verification/{verification_id}",
    response_model=VerificationResponse,
)
def get_verification(
    verification_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a previously stored verification.
    """

    verification = db.get(
        Verification,
        verification_id,
    )

    if verification is None:
        raise HTTPException(
            status_code=404,
            detail="Verification not found.",
        )

    return build_verification_response(verification)


@app.get("/api/history")
def get_history(
    db: Session = Depends(get_db),
):
    """
    Return the most recent verification history.
    """

    statement = (
        select(Verification)
        .join(Verification.claim)
        .order_by(Verification.verified_at.desc())
        .limit(50)
    )

    verifications = db.execute(
        statement
    ).scalars().all()

    return {
        "items": [
            {
                "verification_id": verification.id,
                "claim": verification.claim.original_text,
                "verdict": verification.verdict,
                "confidence": verification.confidence,
                "verified_at": verification.verified_at,
            }
            for verification in verifications
        ]
    }
