"""Evidence-ranked research with digest-bound human approval."""

from .digest import canonical_json, digest
from .evidence import rank_claims
from .gate import ActionGate, Approval, PolicyError
from .models import ActionKind, Claim, Evidence, Outcome
from .proposal import Proposal

__all__ = [
    "ActionGate",
    "ActionKind",
    "Approval",
    "Claim",
    "Evidence",
    "Outcome",
    "PolicyError",
    "Proposal",
    "canonical_json",
    "digest",
    "rank_claims",
]
