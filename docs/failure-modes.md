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

## Unknown action mistaken for read-only
A caller supplies an action string or value that is not a reviewed `ActionKind`. Response: deny; only the explicit read-only enum is exempt from approval.

## Invalid or backward approval clock
A non-finite timestamp, non-positive TTL, or clock rollback would make approval expiry unreliable. Response: refuse granting or authorizing until the timing evidence is valid. The gate is a demonstration, not a durable clock service.
