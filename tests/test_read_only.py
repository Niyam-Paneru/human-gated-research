from research_gate import ActionGate, ActionKind, Evidence, Proposal


def test_read_only_does_not_require_approval():
    proposal = Proposal(
        id="read-1",
        claim_id="c1",
        action=ActionKind.READ_ONLY,
        target="local-review",
        rationale="inspect evidence",
        evidence=(Evidence("source", 1.0, "observed"),),
    )
    ok, reason = ActionGate().authorize(proposal)
    assert ok
    assert reason == "read_only"
