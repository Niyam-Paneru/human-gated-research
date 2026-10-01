from __future__ import annotations

from collections.abc import Sequence

from .models import Claim


def rank_claims(claims: Sequence[Claim]) -> list[Claim]:
    def key(claim: Claim) -> tuple[int, float]:
        newest = max((item.observed_at for item in claim.evidence), default=0.0)
        return claim.independent_source_count, newest

    return sorted(claims, key=key, reverse=True)
