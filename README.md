# Human-Gated Research

Imagine approving an email addressed to Alice. Then the agent quietly swaps Alice for Bob and sends it anyway because the approval ID is still there.

Congratulations: the checkmark has become a souvenir.

This Python module binds approval to the **exact proposal** — its claim, action, target, rationale, evidence, and identity. Change any of those details and the old approval no longer counts.

## What was actually approved?

Approve “send report A to recipient X,” then swap the destination to Y. The gate doesn't shrug and say “close enough”; it returns **proposal_changed_after_approval**.

| Situation | What the gate does |
| --- | --- |
| Missing required evidence | Reject proposal |
| Read-only research, no consequential action | Allow without write approval |
| No approval, expired approval, or used approval | Block the action |
| Proposal altered after review | Block; old content digest no longer matches |
| Exact approved proposal within its one-use window | Eligible for the approved action |

The digest covers the proposal content, not merely an approval ID. An approval also expires and cannot be used for a second consequential action. Ten reposts of one article still count as **one source group**, not ten independent sources.

## The files behind the gate

[Proposal model](src/research_gate/proposal.py) · [digest](src/research_gate/digest.py) · [action gate](src/research_gate/gate.py) · [source grouping](src/research_gate/evidence.py) · [tests and verification](docs/verification.md).

## A very important limitation

Approvals are **in memory** and approved_by is a supplied name, **not authenticated identity**. There's no mail transport, browser, production authorization service, or payment integration here.

It's a rule for an application to enforce, not an application that can safely send things by itself. Approval follows the exact content, not just its ID. [Security notes](SECURITY.md) · [provenance](PROVENANCE.md).
