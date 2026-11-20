# Human-Gated Research

You approve an agent's proposal to send a report to Alice. The agent changes the recipient to Bob but keeps the same green **Approved** badge.

That's not approval. That's a sticker.

This Python module ties approval to the **actual content** — claim, action, target, rationale, evidence, and proposal identity. Change the recipient (or anything else in that digest) and the old approval becomes useless.

## A green checkmark is not a blank cheque

Approve “send report A to recipient X,” then swap the destination to Y. The gate doesn't shrug and say “close enough”; it returns **proposal_changed_after_approval**.

| Situation | What the gate does |
| --- | --- |
| Missing required evidence | Reject proposal |
| Read-only research, no consequential action | Allow without write approval |
| No approval, expired approval, or used approval | Block the action |
| Proposal altered after review | Block; old content digest no longer matches |
| Exact approved proposal within its one-use window | Eligible for the approved action |

The digest covers the proposal, not merely an approval ID. Approval expires and is single-use. And ten articles repeating the same source are still **one source group** — a photocopier is not an eyewitness.

## The files behind the gate

[Proposal model](src/research_gate/proposal.py) · [digest](src/research_gate/digest.py) · [action gate](src/research_gate/gate.py) · [source grouping](src/research_gate/evidence.py) · [tests and verification](docs/verification.md).

## A very important limitation

Approvals are **in memory** and approved_by is a supplied name, **not authenticated identity**. There's no mail transport, browser, production authorization service, or payment integration here.

It's a rule for an application to enforce, not an application that can safely send things by itself. Approval follows the exact content, not just its ID. [Security notes](SECURITY.md) · [provenance](PROVENANCE.md).
