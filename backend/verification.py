from dataclasses import dataclass

from sources import EvidenceSource


SUPPORTED = "SUPPORTED"
PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
UNVERIFIED = "UNVERIFIED"
CONTRADICTED = "CONTRADICTED"
MISLEADING = "MISLEADING"

LOW = "LOW"
MODERATE = "MODERATE"
HIGH = "HIGH"


@dataclass
class VerificationResult:
    verdict: str
    confidence: str
    explanation: str
    evidence: list[EvidenceSource]


def verify_claim(
    claim: str,
    evidence: list[EvidenceSource],
) -> VerificationResult:
    """
    Evaluate a claim against retrieved evidence.

    The engine is intentionally conservative:
    absence of evidence does not become evidence of falsehood.
    """

    if not claim.strip():
        return VerificationResult(
            verdict=UNVERIFIED,
            confidence=LOW,
            explanation="No claim was provided for verification.",
            evidence=[],
        )

    if not evidence:
        return VerificationResult(
            verdict=UNVERIFIED,
            confidence=LOW,
            explanation=(
                "We did not find sufficient reliable evidence to "
                "confirm or contradict this claim."
            ),
            evidence=[],
        )

    supporting = [
        item
        for item in evidence
        if item.relationship.lower() == "supports"
    ]

    contradicting = [
        item
        for item in evidence
        if item.relationship.lower() == "contradicts"
    ]

    contextual = [
        item
        for item in evidence
        if item.relationship.lower() == "adds context"
    ]

    insufficient = [
        item
        for item in evidence
        if item.relationship.lower() == "insufficient"
    ]

    if contradicting and supporting:
        return VerificationResult(
            verdict=PARTIALLY_SUPPORTED,
            confidence=_calculate_confidence(
                supporting,
                contradicting,
            ),
            explanation=(
                "The available evidence is mixed. Some sources "
                "support the claim while other evidence conflicts "
                "with it."
            ),
            evidence=evidence,
        )

    if contradicting:
        return VerificationResult(
            verdict=CONTRADICTED,
            confidence=_calculate_confidence(
                [],
                contradicting,
            ),
            explanation=(
                "Reliable evidence we found conflicts with the "
                "claim."
            ),
            evidence=evidence,
        )

    if supporting and contextual:
        return VerificationResult(
            verdict=PARTIALLY_SUPPORTED,
            confidence=_calculate_confidence(
                supporting,
                [],
            ),
            explanation=(
                "Some available evidence supports the claim, but "
                "additional evidence provides context that limits "
                "or qualifies the claim."
            ),
            evidence=evidence,
        )

    if supporting:
        return VerificationResult(
            verdict=SUPPORTED,
            confidence=_calculate_confidence(
                supporting,
                [],
            ),
            explanation=(
                "The available evidence substantially supports "
                "the claim."
            ),
            evidence=evidence,
        )

    if contextual:
        return VerificationResult(
            verdict=UNVERIFIED,
            confidence=LOW,
            explanation=(
                "The available sources provide context, but we "
                "did not find sufficient evidence to establish "
                "whether the claim is accurate."
            ),
            evidence=evidence,
        )

    if insufficient:
        return VerificationResult(
            verdict=UNVERIFIED,
            confidence=LOW,
            explanation=(
                "The available sources were not sufficient to "
                "confirm or contradict the claim."
            ),
            evidence=evidence,
        )

    return VerificationResult(
        verdict=UNVERIFIED,
        confidence=LOW,
        explanation=(
            "The available evidence was insufficient to "
            "determine whether the claim is accurate."
        ),
        evidence=evidence,
    )


def _calculate_confidence(
    supporting: list[EvidenceSource],
    contradicting: list[EvidenceSource],
) -> str:
    """
    Estimate confidence conservatively from the available evidence.

    This is not a probability and should never be displayed as one.
    """

    evidence_count = len(supporting) + len(contradicting)

    if evidence_count == 0:
        return LOW

    high_quality_count = sum(
        1
        for item in supporting + contradicting
        if item.source_type.lower()
        in {
            "government",
            "official organization",
            "primary source",
            "academic/research",
        }
    )

    if high_quality_count >= 2:
        return HIGH

    if evidence_count >= 2:
        return MODERATE

    return LOW
