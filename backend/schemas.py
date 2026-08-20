from datetime import datetime

from pydantic import BaseModel, Field


class ClaimVerificationRequest(BaseModel):
    claim: str = Field(
        ...,
        min_length=3,
        max_length=5000,
    )


class ArticleVerificationRequest(BaseModel):
    title: str = Field(
        default="",
        max_length=1000,
    )
    publisher: str = Field(
        default="",
        max_length=500,
    )
    url: str = Field(
        ...,
        max_length=4000,
    )
    article_text: str = Field(
        ...,
        min_length=1,
        max_length=100000,
    )
    publication_date: str | None = Field(
        default=None,
        max_length=100,
    )


class EvidenceResponse(BaseModel):
    source_name: str
    source_type: str
    source_url: str
    publication_date: str | None = None
    evidence_text: str
    relationship: str


class VerificationResponse(BaseModel):
    verification_id: int
    claim: str
    normalized_claim: str
    verdict: str
    confidence: str
    explanation: str
    evidence: list[EvidenceResponse]
    verified_at: datetime


class ArticleClaimResult(BaseModel):
    claim: str
    verification_id: int
    verdict: str
    confidence: str
    explanation: str
    evidence: list[EvidenceResponse]


class ArticleVerificationResponse(BaseModel):
    title: str
    publisher: str
    url: str
    claims: list[ArticleClaimResult]


class HealthResponse(BaseModel):
    status: str
    service: str
