# Failure modes

## Proposal changes after approval
The target, rationale, or evidence changes while the id stays the same. Response: digest mismatch blocks the action.

## Approval expires
Circumstances may have changed. Response: require fresh approval.

## Irreversible action is replayed
An already-used approval appears again. Response: refuse the duplicate action.

## Evidence has weak independence
Many citations trace back to the same source group. Response: count independent groups, not raw link count.

## Read-only work gets over-gated
A harmless local inspection would require the same ceremony as an external action. Response: keep read-only work outside the irreversible gate.

## Proposal has no evidence
The system tries to act from unsupported reasoning. Response: proposal creation fails.
