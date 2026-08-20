from dataclasses import dataclass
from datetime import datetime


@dataclass
class EvidenceSource:
    url: str
    domain: str
    publisher: str
    source_type: str
    title: str
    author: str | None
    publication_date: str | None
    evidence_text: str
    relationship: str
    relevance: float | None = None


class EvidenceProvider:
    """
    Base interface for evidence retrieval.

    Real search, news, government, RSS, and other evidence providers
    can implement this interface later.
    """

    name = "base"

    def search(self, claim: str) -> list[EvidenceSource]:
        raise NotImplementedError


class LocalEvidenceProvider(EvidenceProvider):
    """
    Local development provider.

    This intentionally returns no evidence by default.
    It prevents mock information from being presented as real evidence.

    A controlled test provider can be added later for automated testing.
    """

    name = "local"

    def search(self, claim: str) -> list[EvidenceSource]:
        return []


class EvidenceService:
    """
    Coordinates evidence retrieval across configured providers.
    """

    def __init__(
        self,
        providers: list[EvidenceProvider] | None = None,
    ):
        self.providers = providers or [LocalEvidenceProvider()]

    def search(self, claim: str) -> list[EvidenceSource]:
        evidence: list[EvidenceSource] = []

        for provider in self.providers:
            try:
                results = provider.search(claim)

                if results:
                    evidence.extend(results)

            except Exception:
                continue

        return self._deduplicate(evidence)

    @staticmethod
    def _deduplicate(
        evidence: list[EvidenceSource],
    ) -> list[EvidenceSource]:
        seen: set[tuple[str, str]] = set()
        unique: list[EvidenceSource] = []

        for item in evidence:
            key = (
                item.url.strip().lower(),
                item.evidence_text.strip().lower(),
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(item)

        return unique
