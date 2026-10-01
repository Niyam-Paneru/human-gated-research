from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionKind(str, Enum):
    READ_ONLY = "read_only"
    SUBMIT_PUBLIC = "submit_public"
    CONTACT_THIRD_PARTY = "contact_third_party"
    SPEND_MONEY = "spend_money"


IRREVERSIBLE_ACTIONS = frozenset(
    {
        ActionKind.SUBMIT_PUBLIC,
        ActionKind.CONTACT_THIRD_PARTY,
        ActionKind.SPEND_MONEY,
    }
)


class Outcome(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REFUSED = "refused"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"
    ALREADY_ACTED = "already_acted"


@dataclass(frozen=True, slots=True)
class Evidence:
    source: str
    observed_at: float
    summary: str
    independent_group: str = ""

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("evidence requires a source")


@dataclass(frozen=True, slots=True)
class Claim:
    id: str
    statement: str
    evidence: tuple[Evidence, ...] = ()

    @property
    def independent_source_count(self) -> int:
        return len({item.independent_group or item.source for item in self.evidence})
