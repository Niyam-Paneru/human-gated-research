# Human-Gated Research

**An approval authorizes the exact proposal a person reviewed—not whatever keeps the same proposal id later.**

This public Python slice separates low-risk research from actions that change the outside world. Evidence can be ranked and read-only work can proceed without an approval round-trip. For `submit_public`, `contact_third_party`, and `spend_money`, authorization is granted only when a current proposal still matches a named human approval and that approval has not expired or already been used.

```mermaid
sequenceDiagram
    participant R as Research path
    participant G as ActionGate
    participant H as Human reviewer
    participant E as Effect boundary

    R->>G: authorize(read-only action)
    G-->>R: allow read_only; no approval round-trip

    R->>G: propose(evidence + irreversible action)
    G->>G: require evidence
    G-->>R: proposal accepted
    R-->>H: present exact proposal for review
    opt Human approves the exact proposal
        H->>G: approve(proposal, approved_by)
        G->>G: re-check evidence
        G->>G: compute/store payload_digest + TTL
    end

    Note over R,G: Content may change after approval; authorize checks the current digest.
    R->>G: authorize(current proposal)
    alt proposal id already acted
        G-->>R: refuse already_acted
    else no approval exists
        G-->>R: refuse no_approval
    else digest changed after approval
        G-->>R: refuse proposal_changed_after_approval
    else approval expired
        G-->>R: refuse approval_expired
    else live, matching, unused approval
        G->>G: mark proposal id acted
        G-->>R: allow once
        R->>E: cross the effect boundary
    end
```

## The trust boundary

For irreversible actions, the path is:

**evidence → proposal → canonical digest → named human approval → authorization checks → allow once**

`Proposal.payload_digest` hashes a canonical JSON payload containing the proposal id, claim id, action, target, rationale, and normalized evidence. Changing approval-relevant content changes the digest; keeping the same proposal id does not preserve authorization. A proposal id is an identifier, not a reusable permission coupon.

Authorization checks the current state in this order:

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

`ActionGate.propose()` rejects a proposal with no evidence, and `ActionGate.approve()` reuses that same check. Skipping the explicit `propose()` call therefore cannot create an approval for an evidence-free irreversible proposal.

The approval digest includes each evidence item's source, timestamp, summary, and independent group, so changing the evidence grouping also changes the approval identity.

## Where to inspect

- [`src/research_gate/proposal.py`](src/research_gate/proposal.py) — approval-relevant proposal payload.
- [`src/research_gate/digest.py`](src/research_gate/digest.py) — canonical JSON and SHA-256 digest.
- [`src/research_gate/gate.py`](src/research_gate/gate.py) — evidence requirement, approval TTL, refusal paths, replay prevention, and audit history.
- [`src/research_gate/evidence.py`](src/research_gate/evidence.py) — independent-corroboration ranking.
- [`src/research_gate/demo.py`](src/research_gate/demo.py) — runnable walkthrough of mutation, missing approval, replay, expiry, and read-only behavior.

Tests cover evidence-free approval rejection, the read-only bypass, missing approval, mutation after approval, expiry, replay refusal, one-time allowance, and the named-approver requirement.

Verification commands and expected checks: [`docs/verification.md`](docs/verification.md).

## What approval does not prove

This repository demonstrates approval semantics, not a production authorization service. Approvals, acted ids, and audit history are in-memory; the approver name is not authenticated; and the repo contains no browser credentials, payment method, email account, or external-action transport.

See [`SECURITY.md`](SECURITY.md) for production-boundary requirements and [`PROVENANCE.md`](PROVENANCE.md) for what was preserved or removed from the private systems that inspired this public slice.
