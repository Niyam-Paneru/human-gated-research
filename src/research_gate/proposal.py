from __future__ import annotations

from dataclasses import dataclass

from .digest import digest
from .models import ActionKind, Evidence


@dataclass(frozen=True, slots=True)
class Proposal:
    id: str
    claim_id: str
    action: ActionKind
    target: str
    rationale: str
    evidence: tuple[Evidence, ...] = ()

    def to_payload(self) -> dict[str, object]:
        ordered = sorted(
            self.evidence,
            key=lambda item: (item.independent_group, item.source, item.observed_at),
        )
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "action": self.action.value,
            "target": self.target,
            "rationale": self.rationale,
            "evidence": [
                {
                    "source": item.source,
                    "observed_at": item.observed_at,
                    "summary": item.summary,
                }
                for item in ordered
            ],
        }

    @property
    def payload_digest(self) -> str:
        return digest(self.to_payload())
