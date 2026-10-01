# Human-Gated Research

**An approval authorizes the exact proposal a person reviewed—not whatever keeps the same proposal id later.**

This public Python slice separates low-risk research from actions that change the outside world. Evidence can be ranked and read-only work can proceed without an approval round-trip. For `submit_public`, `contact_third_party`, and `spend_money`, authorization is granted only when a current proposal still matches a named human approval and that approval has not expired or already been used.

![Human-gated authorization flow](docs/workflow.svg)

## The trust boundary

For irreversible actions, the path is:

**evidence → proposal → canonical digest → named human approval → authorization checks → allow once**

`Proposal.payload_digest` hashes a canonical JSON payload containing the proposal id, claim id, action, target, rationale, and normalized evidence. Changing approval-relevant content changes the digest; keeping the same proposal id does not preserve authorization.

Authorization then checks the current state in this order:

| Check | Result |
|---|---|
| Action is read-only | allow immediately and record `read_only`; no human approval required |
| Proposal id already acted | refuse with `already_acted` |
| No approval exists | refuse with `no_approval` |
| Approved digest differs from current digest | refuse with `proposal_changed_after_approval` |
| Approval is older than its TTL | refuse with `approval_expired` |
| All irreversible-action checks pass | mark the proposal id acted, record approval, allow once |

Approval also requires a non-empty `approved_by` value. In this demo that value names the approver; it does **not** authenticate the person's identity.

## Evidence before action

`rank_claims()` prefers the number of **independent source groups** and uses newest evidence only as a tie-breaker. Multiple citations assigned to the same independent group count once.

`ActionGate.propose()` rejects a proposal with no evidence. The approval digest includes each evidence item's source, timestamp, summary, and independent group, so changing the evidence grouping also changes the approval identity.

## Where to inspect

- [`src/research_gate/proposal.py`](src/research_gate/proposal.py) — approval-relevant proposal payload.
- [`src/research_gate/digest.py`](src/research_gate/digest.py) — canonical JSON and SHA-256 digest.
- [`src/research_gate/gate.py`](src/research_gate/gate.py) — approval TTL, refusal paths, replay prevention, and audit history.
- [`src/research_gate/evidence.py`](src/research_gate/evidence.py) — independent-corroboration ranking.
- [`src/research_gate/demo.py`](src/research_gate/demo.py) — runnable walkthrough of mutation, missing approval, replay, expiry, and read-only behavior.

## Verify it

From the repository root with Python 3.10+ and `pytest` installed:

```bash
python -m pytest
PYTHONPATH=src python -m research_gate.demo
```

CircleCI additionally compiles `src/` and checks that the public proof files are present.

The diagram's decision states are covered directly by tests:

| Diagram state | Test |
|---|---|
| read-only bypass | `test_read_only_does_not_require_approval` |
| no approval | `test_an_unapproved_irreversible_action_is_refused` |
| changed proposal / digest mismatch | `test_editing_a_proposal_after_approval_invalidates_it` |
| expired approval | `test_an_expired_approval_is_refused` |
| replay / already acted | `test_an_action_cannot_be_replayed` |
| allowed once | `test_an_approved_action_proceeds` |
| named approver required | `test_an_approval_must_name_a_person` |

## Boundary and provenance

This repository demonstrates approval semantics, not a production authorization service. Approvals, acted ids, and audit history are in-memory; the approver name is not authenticated; and the repo contains no browser credentials, payment method, email account, or external-action transport.

See [`SECURITY.md`](SECURITY.md) for production-boundary requirements and [`PROVENANCE.md`](PROVENANCE.md) for what was preserved or removed from the private systems that inspired this public slice.
