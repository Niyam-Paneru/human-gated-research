# Human-Gated Research

Evidence-backed research with approval tied to the exact proposal a person reviewed. Read-only work can proceed; consequential actions require a current, matching, unused approval.

**A proposal id is not a reusable permission coupon.**

This public sample comes from my private research and acquisition tooling. It makes evidence ranking and approval semantics reviewable; I can build and adapt the surrounding research applications, review workflows, and connectors for different requirements.

## Review: approve the content, not just the id

```mermaid
sequenceDiagram
    participant R as Research path
    participant G as ActionGate
    participant H as Human reviewer
    R->>G: <b>Propose with evidence</b>
    alt Evidence missing
        G-->>R: <b>Reject proposal</b>
    else Evidence present
        G-->>R: Proposal accepted
        R-->>H: Present exact proposal
        opt Human approves
            H->>G: approve(proposal, approved_by)
            G->>G: Require evidence + named person
            G->>G: <b>Store digest + TTL</b>
        end
    end
    Note over R,G: authorize checks the current content digest
```

## Authorization: check again at the action boundary

`submit_public`, `contact_third_party`, and `spend_money` take the approval path below. The caller owns the external action after the gate returns.

```mermaid
flowchart LR
    A["<b>Current proposal</b>"] --> R{"Read-only?"}
    R -- Yes --> L["<b>Allow</b><br/>read_only"]
    R -- No --> G{"Approval checks pass?"}
    G -- No --> X["<b>Refuse</b><br/>used, missing,<br/>changed or expired"]
    G -- Yes --> O["<b>Mark acted</b><br/>Allow once"]
    classDef input fill:#e8e6df,stroke:#55534a,color:#20201d,stroke-width:2px;
    classDef pass fill:#d2e5d8,stroke:#38734d,color:#183923,stroke-width:2px;
    classDef stop fill:#f4dadd,stroke:#b14253,color:#611c29,stroke-width:2px;
    class A,R,G input;
    class L,O pass;
    class X stop;
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
