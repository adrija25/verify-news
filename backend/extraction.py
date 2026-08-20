import re


def normalize_text(text: str) -> str:
    """
    Normalize text without changing its underlying meaning.
    """

    if not text:
        return ""

    normalized = text.strip()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.strip(" \t\n\r\"'")

    return normalized


def split_into_sentences(text: str) -> list[str]:
    """
    Split article text into readable sentence-level units.

    This is intentionally conservative and uses only local text
    processing. It does not invent facts or use an external AI API.
    """

    normalized = normalize_text(text)

    if not normalized:
        return []

    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", normalized)

    sentences = []

    for part in parts:
        sentence = normalize_text(part)

        if not sentence:
            continue

        if len(sentence) < 25:
            continue

        sentences.append(sentence)

    return sentences


def looks_like_claim(text: str) -> bool:
    """
    Identify sentences that are reasonably likely to contain
    a factual claim.

    Questions, very short fragments, and obvious headings are
    excluded.
    """

    normalized = normalize_text(text)

    if not normalized:
        return False

    if normalized.endswith("?"):
        return False

    if len(normalized) < 25:
        return False

    words = normalized.split()

    if len(words) < 5:
        return False

    claim_indicators = (
        " is ",
        " are ",
        " was ",
        " were ",
        " has ",
        " have ",
        " had ",
        " will ",
        " can ",
        " could ",
        " said ",
        " says ",
        " reported ",
        " announced ",
        " confirmed ",
        " according ",
        " found ",
        " shows ",
        " showed ",
        " happened ",
        " occurred ",
        " died ",
        " won ",
        " lost ",
        " increased ",
        " decreased ",
        " reached ",
        " became ",
    )

    padded = f" {normalized.lower()} "

    return any(indicator in padded for indicator in claim_indicators)


def extract_claims(text: str, max_claims: int = 5) -> list[dict]:
    """
    Extract a small number of likely factual claims from article text.

    This is a deterministic v1 extractor.

    It does not:
    - invent claims
    - rewrite claims
    - verify claims
    - call external APIs
    - use an AI model

    It simply identifies useful sentence-level factual statements
    that can later be sent through the verification pipeline.
    """

    if not text:
        return []

    sentences = split_into_sentences(text)

    claims = []

    for sentence in sentences:
        if not looks_like_claim(sentence):
            continue

        prepared = prepare_claim(sentence)

        claims.append(prepared)

        if len(claims) >= max_claims:
            break

    return claims


def extract_claim_texts(text: str, max_claims: int = 5) -> list[str]:
    """
    Convenience helper returning only the extracted claim text.
    """

    claims = extract_claims(text, max_claims=max_claims)

    return [
        claim["original_text"]
        for claim in claims
    ]


def extract_claim_date(text: str) -> str | None:
    """
    Extract a simple explicit date from a claim when one is present.

    Supported formats are intentionally limited in v1.
    """

    if not text:
        return None

    patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",
        r"\b\d{1,2}-\d{1,2}-\d{4}\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(0)

    return None


def prepare_claim(text: str) -> dict:
    """
    Prepare a claim or article text for the verification pipeline.

    This function remains compatible with the existing verification
    pipeline while adding basic claim metadata extraction.
    """

    original_text = text.strip() if text else ""
    normalized_text = normalize_text(original_text)

    return {
        "original_text": original_text,
        "normalized_text": normalized_text,
        "subject": None,
        "event": None,
        "location": None,
        "claim_date": extract_claim_date(normalized_text),
    }
