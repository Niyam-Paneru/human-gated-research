from research_gate import ActionKind, Evidence, Proposal


def proposal(evidence):
    return Proposal(
        id="p",
        claim_id="c",
        action=ActionKind.CONTACT_THIRD_PARTY,
        target="https://example.test/contact",
        rationale="reviewed rationale",
        evidence=evidence,
    )


def test_evidence_order_does_not_change_digest():
    evidence = (
        Evidence("a", 1.0, "a"),
        Evidence("b", 2.0, "b"),
    )
    assert proposal(evidence).payload_digest == proposal(tuple(reversed(evidence))).payload_digest


def test_target_change_changes_digest():
    evidence = (Evidence("a", 1.0, "a"),)
    a = proposal(evidence)
    b = Proposal(
        id=a.id,
        claim_id=a.claim_id,
        action=a.action,
        target="https://other.example/contact",
        rationale=a.rationale,
        evidence=a.evidence,
    )
    assert a.payload_digest != b.payload_digest
