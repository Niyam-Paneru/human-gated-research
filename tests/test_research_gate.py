from __future__ import annotations

import pytest

from research_gate import (
    ActionGate,
    ActionKind,
    Claim,
    Evidence,
    Outcome,
    PolicyError,
    Proposal,
    rank_claims,
)


def ev(source: str, group: str = "", day: int = 1) -> Evidence:
    return Evidence(
        source=source,
        observed_at=float(day),
        summary=f"observation from {source}",
        independent_group=group,
    )


def proposal(**over) -> Proposal:
    base = dict(
        id="p1",
        claim_id="c1",
        action=ActionKind.CONTACT_THIRD_PARTY,
        target="https://vendor.example/contact",
        rationale="Vendor appears to be the only one meeting the constraint.",
        evidence=(ev("registry-a"), ev("registry-b", day=2)),
    )
    base.update(over)
    return Proposal(**base)


# --- evidence integrity ----------------------------------------------------


def test_evidence_requires_a_source() -> None:
    with pytest.raises(ValueError):
        Evidence(source="   ", observed_at=1.0, summary="trust me")


def test_corroboration_counts_independent_groups_not_items() -> None:
    """Five citations from one syndicated story are one source, not five."""
    claim = Claim(
        id="c1",
        statement="Vendor is sole compliant supplier",
        evidence=(
            ev("wire-a", group="wire"),
            ev("wire-b", group="wire"),
            ev("wire-c", group="wire"),
            ev("registry", group="registry"),
        ),
    )
    assert claim.independent_source_count == 2


def test_ranking_prefers_corroboration_over_recency() -> None:
    stale_but_corroborated = Claim(
        id="c1", statement="a", evidence=(ev("s1", "g1", day=1), ev("s2", "g2", day=1))
    )
    fresh_but_unsourced = Claim(id="c2", statement="b", evidence=(ev("blog", day=99),))
    ranked = rank_claims([fresh_but_unsourced, stale_but_corroborated])
    assert ranked[0].id == "c1", "one corroborated old source beats one fresh rumour"


# --- approval binding ------------------------------------------------------


def test_a_proposal_cannot_be_proposed_without_evidence() -> None:
    with pytest.raises(PolicyError):
        ActionGate().propose(proposal(evidence=()))


def test_approval_cannot_bypass_the_evidence_requirement() -> None:
    with pytest.raises(PolicyError, match="carries no evidence"):
        ActionGate().approve(proposal(evidence=()), approved_by="operator")


def test_an_approval_must_name_a_person() -> None:
    gate = ActionGate()
    with pytest.raises(PolicyError):
        gate.approve(proposal(), approved_by="  ")


def test_an_unapproved_irreversible_action_is_refused() -> None:
    ok, reason = ActionGate().authorize(proposal())
    assert not ok
    assert reason == "no_approval"


def test_an_approved_action_proceeds() -> None:
    gate = ActionGate()
    p = proposal()
    gate.approve(p, approved_by="operator")
    ok, reason = gate.authorize(p)
    assert ok
    assert reason == "approved"


def test_editing_a_proposal_after_approval_invalidates_it() -> None:
    """The most important test here: approval must bind to content, not to an id."""
    gate = ActionGate()
    original = proposal()
    gate.approve(original, approved_by="operator")

    edited = original.__class__(
        **{
            **{f.name: getattr(original, f.name) for f in original.__dataclass_fields__.values()},
            "target": "https://someone-else.example/contact",
        }
    )

    ok, reason = gate.authorize(edited)
    assert not ok
    assert reason == "proposal_changed_after_approval"


def test_an_expired_approval_is_refused() -> None:
    clock = {"t": 1_000.0}
    gate = ActionGate(ttl_seconds=60.0, now=lambda: clock["t"])
    p = proposal()
    gate.approve(p, approved_by="operator")

    clock["t"] += 61.0
    ok, reason = gate.authorize(p)
    assert not ok
    assert reason == "approval_expired"


def test_an_action_cannot_be_replayed() -> None:
    gate = ActionGate()
    p = proposal()
    gate.approve(p, approved_by="operator")
    assert gate.authorize(p)[0] is True
    ok, reason = gate.authorize(p)
    assert not ok
    assert reason == "already_acted"


def test_a_different_proposal_does_not_inherit_an_approval() -> None:
    gate = ActionGate()
    gate.approve(proposal(id="p1"), approved_by="operator")
    ok, reason = gate.authorize(proposal(id="p2"))
    assert not ok
    assert reason == "no_approval"


# --- audit -----------------------------------------------------------------


def test_every_decision_is_recorded() -> None:
    gate = ActionGate()
    p = proposal()
    gate.authorize(p)          # refused: no approval
    gate.approve(p, "operator")
    gate.authorize(p)          # allowed
    gate.authorize(p)          # refused: replay

    outcomes = [outcome for _, outcome, _ in gate.audit()]
    assert outcomes == [
        Outcome.REFUSED,        # no approval yet
        Outcome.APPROVED,       # the approval itself
        Outcome.APPROVED,       # the action was permitted
        Outcome.ALREADY_ACTED,  # replay refused, tracked separately
    ]


def test_digest_is_stable_across_key_and_evidence_ordering() -> None:
    """Two reviewers listing the same sources differently must agree on the digest."""
    a = proposal()
    b = Proposal(
        id=a.id,
        claim_id=a.claim_id,
        action=a.action,
        target=a.target,
        rationale=a.rationale,
        evidence=tuple(reversed(a.evidence)),
    )
    assert a.payload_digest == b.payload_digest


def test_digest_changes_when_the_target_changes() -> None:
    a = proposal()
    b = proposal(target="https://someone-else.example/contact")
    assert a.payload_digest != b.payload_digest
