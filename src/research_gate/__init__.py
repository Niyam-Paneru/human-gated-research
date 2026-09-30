"""Evidence-ranked research with human-gated action.

An agent that gathers information and an agent that acts on the world are
different capabilities with different risk profiles. Mixing them is how a
research tool becomes an incident.

This module separates the two explicitly:

    gather -> rank -> propose  ...  human decides  ...  act

Three properties do the work:

1.  A proposal is a *proposal*. Acting on it requires a signed approval whose
    payload digest matches the proposal exactly. Editing the plan after
    approval invalidates the approval.

2.  Ranking is by evidence, not by confidence. A claim with three independent
    sources outranks a claim the model is very sure about with none, because
    confidence is not observable and sourcing is.

3.  Every external action is refused unless it is both approved and attached to
    a live approval. Approval has a TTL, so an approval cannot be replayed a
    week later against changed circumstances.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Callable, Iterable, Mapping, Sequence


class ActionKind(str, Enum):
    """What kind of world change is being requested."""

    READ_ONLY = "read_only"
    SUBMIT_PUBLIC = "submit_public"
    CONTACT_THIRD_PARTY = "contact_third_party"
    SPEND_MONEY = "spend_money"


class Outcome(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REFUSED = "refused"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"
    ALREADY_ACTED = "already_acted"


#: Actions that can change something a third party will observe.
#: These are never performed without a live, digest-matched approval.
IRREVERSIBLE_ACTIONS = frozenset(
    {
        ActionKind.SUBMIT_PUBLIC,
        ActionKind.CONTACT_THIRD_PARTY,
        ActionKind.SPEND_MONEY,
    }
)


@dataclass(frozen=True, slots=True)
class Evidence:
    """One supporting observation.

    `source` is the only field that makes a claim auditable. A claim with no
    source is an opinion wearing a fact's clothes.
    """

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
        """Count distinct source groups, not evidence items.

        Five citations from one syndicated wire story are one source. Counting
        items overstates corroboration, which is the specific failure this
        guards against.
        """
        return len({e.independent_group or e.source for e in self.evidence})


def rank_claims(claims: Sequence[Claim]) -> list[Claim]:
    """Rank by independent corroboration, then by recency of best evidence.

    Deliberately not a confidence score. Confidence is the model's opinion about
    its own reliability, which no caller can audit.
    """
    def key(claim: Claim) -> tuple:
        newest = max((e.observed_at for e in claim.evidence), default=0.0)
        return (claim.independent_source_count, newest)

    return sorted(claims, key=key, reverse=True)


def canonical_json(payload: Mapping[str, object]) -> str:
    """Stable serialisation so a digest is comparable across processes."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def digest(payload: Mapping[str, object]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Proposal:
    """A suggested action plus everything a reviewer needs to judge it."""

    id: str
    claim_id: str
    action: ActionKind
    target: str
    rationale: str
    evidence: tuple[Evidence, ...] = ()

    def to_payload(self) -> dict[str, object]:
        # Evidence is sorted before serialisation. Two reviewers who read the
        # same sources in a different order are looking at the same proposal,
        # and must produce the same digest -- otherwise approval binding breaks
        # for reasons that have nothing to do with the content.
        ordered = sorted(self.evidence, key=lambda e: (e.independent_group, e.source, e.observed_at))
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "action": self.action.value,
            "target": self.target,
            "rationale": self.rationale,
            "evidence": [
                {
                    "source": e.source,
                    "observed_at": e.observed_at,
                    "summary": e.summary,
                }
                for e in ordered
            ],
        }

    @property
    def payload_digest(self) -> str:
        return digest(self.to_payload())


@dataclass(frozen=True, slots=True)
class Approval:
    """A human decision, bound to one exact proposal digest."""

    proposal_id: str
    payload_digest: str
    approved_by: str
    granted_at: float
    ttl_seconds: float = 86_400.0


class PolicyError(Exception):
    pass


@dataclass
class ActionGate:
    """The only path to an irreversible effect.

    Every irreversible action passes through `authorize`, which requires a live
    approval matching the proposal's current digest. There is no `force` flag
    and no override, because an override is just an unlogged bypass.
    """

    ttl_seconds: float = 86_400.0
    now: Callable[[], float] = time.time
    _approvals: dict[str, Approval] = field(default_factory=dict)
    _acted: set[str] = field(default_factory=set)
    _history: list[tuple[str, Outcome, str]] = field(default_factory=list)

    def propose(self, proposal: Proposal) -> Proposal:
        if not proposal.evidence:
            raise PolicyError(f"proposal {proposal.id} carries no evidence")
        return proposal

    def approve(self, proposal: Proposal, approved_by: str) -> Approval:
        if not approved_by.strip():
            raise PolicyError("an approval must name a person")
        approval = Approval(
            proposal_id=proposal.id,
            payload_digest=proposal.payload_digest,
            approved_by=approved_by,
            granted_at=self.now(),
            ttl_seconds=self.ttl_seconds,
        )
        self._approvals[proposal.id] = approval
        self._history.append((proposal.id, Outcome.APPROVED, approved_by))
        return approval

    def _record(self, proposal_id: str, outcome: Outcome) -> None:
        self._history.append((proposal_id, outcome, ""))

    def authorize(self, proposal: Proposal) -> tuple[bool, str]:
        """Returns (permitted, reason). Never raises for ordinary refusals."""
        approval = self._approvals.get(proposal.id)

        if proposal.id in self._acted:
            self._record(proposal.id, Outcome.ALREADY_ACTED)
            return False, "already_acted"

        if approval is None:
            self._record(proposal.id, Outcome.REFUSED)
            return False, "no_approval"

        # A proposal edited after approval no longer matches it.
        if approval.payload_digest != proposal.payload_digest:
            self._record(proposal.id, Outcome.SUPERSEDED)
            return False, "proposal_changed_after_approval"

        if self.now() - approval.granted_at > approval.ttl_seconds:
            self._record(proposal.id, Outcome.EXPIRED)
            return False, "approval_expired"

        self._acted.add(proposal.id)
        self._record(proposal.id, Outcome.APPROVED)
        return True, "approved"

    def audit(self) -> list[tuple[str, Outcome, str]]:
        return list(self._history)
