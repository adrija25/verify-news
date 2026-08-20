from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class EvidenceItem:
    """
    Internal representation of one piece of evidence.

    No evidence is considered real unless it comes from an actual
    configured source.
    """

    url: str
    domain: str
    publisher: str | None
    source_type: str
    title: str | None
    author: str | None
    publication_date: str | None
    evidence_text: str
    relationship: str
    relevance: float | None = None


class EvidenceService:
    """
    Evidence retrieval layer.

    The initial implementation deliberately performs no external
    searches. This keeps the local prototype honest and prevents
    fabricated evidence.

    Real search/news/government source adapters will be connected
    here later.
    """

    def __init__(self):
        self.adapters = []

    def search(self, claim: str) -> list[EvidenceItem]:
        """
        Search configured evidence sources.

        Returns an empty list until a real evidence adapter is
        configured.
        """

        if not claim or not claim.strip():
            return []

        evidence = []

        for adapter in self.adapters:
            try:
                results = adapter.search(claim)

                if results:
                    evidence.extend(results)

            except Exception:
                # A failed external source must not break the
                # entire verification request.
                continue

        return evidence

    def add_adapter(self, adapter) -> None:
        """
        Register a real evidence/search adapter.

        Adapters must expose:

            search(claim) -> list[EvidenceItem]
        """

        if adapter not in self.adapters:
            self.adapters.append(adapter)


def build_evidence_item(
    url: str,
    evidence_text: str,
    relationship: str,
    source_type: str = "Unknown",
    publisher: str | None = None,
    title: str | None = None,
    author: str | None = None,
    publication_date: str | None = None,
    relevance: float | None = None,
) -> EvidenceItem:
    """
    Construct an EvidenceItem safely from source information.
    """

    parsed_url = urlparse(url)

    domain = parsed_url.netloc.lower()

    if domain.startswith("www."):
        domain = domain[4:]

    return EvidenceItem(
        url=url,
        domain=domain,
        publisher=publisher,
        source_type=source_type,
        title=title,
        author=author,
        publication_date=publication_date,
        evidence_text=evidence_text,
        relationship=relationship,
        relevance=relevance,
    )
