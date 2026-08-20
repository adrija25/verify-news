from sources import EvidenceSource
from verification import (
    CONTRADICTED,
    MISLEADING,
    PARTIALLY_SUPPORTED,
    SUPPORTED,
    UNVERIFIED,
)


def analyze_evidence(
    claim: str,
    evidence: list[EvidenceSource],
) -> dict:
    """
    Analyze the available evidence before the final verification
    result is constructed.

    This layer deliberately does not invent evidence or infer
    certainty when reliable evidence is unavailable.
    """

    if not evidence:
        return {
            "supporting_count": 0,
            "contradicting_count": 0,
            "context_count": 0,
            "insufficient_count": 0,
            "has_primary_evidence": False,
            "has_mixed_evidence": False,
        }

    supporting_count = sum(
        1
        for item in evidence
        if item.relationship.lower() == "supports"
    )

    contradicting_count = sum(
        1
        for item in evidence
        if item.relationship.lower() == "contradicts"
    )

    context_count = sum(
        1
        for item in evidence
        if item.relationship.lower() == "adds context"
    )

    insufficient_count = sum(
        1
        for item in evidence
        if item.relationship.lower() == "insufficient"
    )

    has_primary_evidence = any(
        item.source_type.lower()
        in {
            "government",
            "official organization",
            "primary source",
        }
        for item in evidence
    )

    return {
        "supporting_count": supporting_count,
        "contradicting_count": contradicting_count,
        "context_count": context_count,
        "insufficient_count": insufficient_count,
        "has_primary_evidence": has_primary_evidence,
        "has_mixed_evidence": (
            supporting_count > 0 and contradicting_count > 0
        ),
    }


def determine_relationship(
    evidence_text: str,
    supports_claim: bool | None,
) -> str:
    """
    Convert an already-evaluated evidence relationship into one of
    the product's controlled relationship values.

    This function does not decide whether evidence supports a claim.
    That determination must come from a real evidence evaluation
    process.
    """

    if supports_claim is True:
        return "Supports"

    if supports_claim is False:
        return "Contradicts"

    if evidence_text.strip():
        return "Adds context"

    return "Insufficient"


def build_explanation(
    verdict: str,
    analysis: dict,
) -> str:
    """
    Generate a concise explanation from structured evidence analysis.
    """

    supporting = analysis["supporting_count"]
    contradicting = analysis["contradicting_count"]
    context = analysis["context_count"]

    if verdict == SUPPORTED:
        return (
            f"The available evidence substantially supports the claim. "
            f"We identified {supporting} supporting evidence item(s)."
        )

    if verdict == CONTRADICTED:
        return (
            f"The available evidence conflicts with the claim. "
            f"We identified {contradicting} contradicting evidence item(s)."
        )

    if verdict == PARTIALLY_SUPPORTED:
        return (
            "Some important elements of the claim are supported, "
            "but the available evidence also provides information "
            "that limits or qualifies the claim."
        )

    if verdict == MISLEADING:
        return (
            "The claim may contain factual elements, but the available "
            "evidence indicates that its framing could create a materially "
            "misleading impression."
        )

    if context:
        return (
            "The available sources provide relevant context, but they "
            "do not establish enough evidence to confirm or contradict "
            "the claim."
        )

    return (
        "We did not find sufficient reliable evidence to confirm or "
        "contradict this claim."
    )
