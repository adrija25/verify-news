import re


def normalize_claim(text: str) -> str:
    """
    Normalize claim text while preserving its meaning.
    The original user-provided text should always be stored separately.
    """
    if not text:
        return ""

    normalized = text.strip()

    normalized = re.sub(r"\s+", " ", normalized)

    normalized = re.sub(r"[!?]+$", ".", normalized)

    if normalized and normalized[-1] not in ".;:":
        normalized += "."

    return normalized


def extract_claim_components(text: str) -> dict:
    """
    Extract basic claim components without pretending to perform
    full semantic understanding.

    More sophisticated claim extraction can be introduced later.
    """
    normalized = normalize_claim(text)

    components = {
        "subject": None,
        "event": None,
        "location": None,
        "claim_date": None,
    }

    if not normalized:
        return components

    components["subject"] = _extract_subject(normalized)
    components["event"] = _extract_event(normalized)
    components["location"] = _extract_location(normalized)
    components["claim_date"] = _extract_date(normalized)

    return components


def _extract_subject(text: str) -> str | None:
    """
    Make a conservative attempt to identify the beginning of the claim
    as its subject.

    This is intentionally simple for v1.
    """
    match = re.match(
        r"^(?:the|a|an)?\s*([A-Z][A-Za-z0-9&.'-]*(?:\s+[A-Z][A-Za-z0-9&.'-]*){0,5})",
        text,
    )

    if match:
        return match.group(1).strip()

    return None


def _extract_event(text: str) -> str | None:
    """
    Identify a likely action/event phrase using common factual verbs.
    """
    event_pattern = re.compile(
        r"\b("
        r"announced|approved|banned|confirmed|denied|introduced|"
        r"launched|passed|rejected|reported|required|restricted|"
        r"signed|started|stopped|won|lost|increased|decreased|"
        r"will|has|have|had|is|are|was|were"
        r")\b",
        re.IGNORECASE,
    )

    match = event_pattern.search(text)

    if match:
        return match.group(1).lower()

    return None


def _extract_location(text: str) -> str | None:
    """
    Detect a small set of common location expressions.
    """
    patterns = [
        r"\bin ([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})",
        r"\bin the ([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})",
        r"\bacross ([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})",
        r"\bnationwide\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            if match.lastindex:
                return match.group(1).strip()

            return "nationwide"

    return None


def _extract_date(text: str) -> str | None:
    """
    Detect common explicit date/year expressions.
    """
    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b(?:19|20)\d{2}\b",
        r"\b(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(0)

    return None


def prepare_claim(text: str) -> dict:
    """
    Prepare a claim for the verification pipeline.
    """
    original_text = text.strip() if text else ""
    normalized_text = normalize_claim(original_text)
    components = extract_claim_components(normalized_text)

    return {
        "original_text": original_text,
        "normalized_text": normalized_text,
        **components,
    }
