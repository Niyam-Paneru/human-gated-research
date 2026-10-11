# Invariants

1. **Irreversible actions require human approval.**
2. **Approval binds to the exact proposal digest.**
3. **Changed proposal content invalidates old approval.**
4. **Approval expires.**
5. **An approval cannot authorize the same irreversible action twice.**
6. **Read-only work stays outside the expensive approval path.**
7. **Evidence ranking uses independent corroboration, not raw citation count.**

8. **Only an explicit `ActionKind.READ_ONLY` is read-only.** Unknown actions fail closed at proposal and authorization; a malformed action cannot inherit read-only permission.
9. **Approval clocks fail closed.** Approval TTL and grant time must be finite and valid; a backward or non-finite authorization clock cannot extend an approval.

The human approves a proposal, not an identifier.
