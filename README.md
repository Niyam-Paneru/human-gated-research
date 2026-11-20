# Human-Gated Research

A research agent drafts an email. A human approves it. Then someone changes the recipient.

The reviewer approved the original proposal, not the revised one.

This Python module binds approval to the **exact proposal**: its claim, action, target, rationale, evidence, and proposal identity. Change those details and the old approval no longer fits.

## What happens if the proposal changes?

A reviewer approves “send report A to recipient X.” The proposal is changed to recipient Y.

The result isn't “close enough.” It's **proposal_changed_after_approval**.

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
