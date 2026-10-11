from __future__ import annotations

import time
from math import isfinite
from dataclasses import dataclass, field
from typing import Callable

from .models import ActionKind, Outcome
from .proposal import Proposal


@dataclass(frozen=True, slots=True)
class Approval:
    proposal_id: str
    payload_digest: str
    approved_by: str
    granted_at: float
    ttl_seconds: float = 86_400.0


class PolicyError(Exception):
    pass


def _finite_number(value: object) -> bool:
    return type(value) in (int, float) and isfinite(value)


def _valid_ttl(value: object) -> bool:
    return _finite_number(value) and value > 0


@dataclass
class ActionGate:
    ttl_seconds: float = 86_400.0
    now: Callable[[], float] = time.time
    _approvals: dict[str, Approval] = field(default_factory=dict)
    _acted: set[str] = field(default_factory=set)
    _history: list[tuple[str, Outcome, str]] = field(default_factory=list)

    def propose(self, proposal: Proposal) -> Proposal:
        if not isinstance(proposal.action, ActionKind):
            raise PolicyError("unsupported_action")
        if not proposal.evidence:
            raise PolicyError(f"proposal {proposal.id} carries no evidence")
        return proposal

    def approve(self, proposal: Proposal, approved_by: str) -> Approval:
        if not approved_by.strip():
            raise PolicyError("an approval must name a person")

        # Approval is a public entry point too. Reuse the proposal invariant here
        # so callers cannot bypass the evidence requirement by skipping propose().
        self.propose(proposal)

        granted_at = self.now()
        if not _finite_number(granted_at) or not _valid_ttl(self.ttl_seconds):
            raise PolicyError("invalid_approval_timing")

        approval = Approval(
            proposal_id=proposal.id,
            payload_digest=proposal.payload_digest,
            approved_by=approved_by,
            granted_at=granted_at,
            ttl_seconds=self.ttl_seconds,
        )
        self._approvals[proposal.id] = approval
        self._history.append((proposal.id, Outcome.APPROVED, approved_by))
        return approval

    def _record(self, proposal_id: str, outcome: Outcome) -> None:
        self._history.append((proposal_id, outcome, ""))

    def authorize(self, proposal: Proposal) -> tuple[bool, str]:
        # No unknown future or malformed action may fall into the read-only path.
        # ActionKind is a string Enum, so equality alone is insufficient here.
        if not isinstance(proposal.action, ActionKind):
            self._record(proposal.id, Outcome.REFUSED)
            return False, "unsupported_action"
        if proposal.action is ActionKind.READ_ONLY:
            self._record(proposal.id, Outcome.READ_ONLY)
            return True, "read_only"

        approval = self._approvals.get(proposal.id)

        if proposal.id in self._acted:
            self._record(proposal.id, Outcome.ALREADY_ACTED)
            return False, "already_acted"

        if approval is None:
            self._record(proposal.id, Outcome.REFUSED)
            return False, "no_approval"

        if approval.payload_digest != proposal.payload_digest:
            self._record(proposal.id, Outcome.SUPERSEDED)
            return False, "proposal_changed_after_approval"

        current_time = self.now()
        if (
            not _finite_number(current_time)
            or not _finite_number(approval.granted_at)
            or not _valid_ttl(approval.ttl_seconds)
            or current_time < approval.granted_at
        ):
            self._record(proposal.id, Outcome.REFUSED)
            return False, "invalid_approval_clock"

        if current_time - approval.granted_at > approval.ttl_seconds:
            self._record(proposal.id, Outcome.EXPIRED)
            return False, "approval_expired"

        self._acted.add(proposal.id)
        self._record(proposal.id, Outcome.APPROVED)
        return True, "approved"

    def audit(self) -> list[tuple[str, Outcome, str]]:
        return list(self._history)
