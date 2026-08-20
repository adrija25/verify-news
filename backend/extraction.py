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


def prepare_claim(text: str) -> dict:
    """
    Prepare a claim or article text for the verification pipeline.

    This is intentionally conservative in v1.
    It does not invent facts or rewrite the user's meaning.
    """

    original_text = text.strip() if text else ""
    normalized_text = normalize_text(original_text)

    return {
        "original_text": original_text,
        "normalized_text": normalized_text,
        "subject": None,
        "event": None,
        "location": None,
        "claim_date": None,
    }
