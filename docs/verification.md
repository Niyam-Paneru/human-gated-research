# Verification

Run from the repository root with Python 3.10+ and `pytest` installed.

```bash
python -m pytest
PYTHONPATH=src python -m research_gate.demo
```

The behavior suite covers the authorization boundary directly:

| Behavior | Test |
|---|---|
| evidence-free approval blocked | `test_approval_cannot_bypass_the_evidence_requirement` |
| read-only bypass | `test_read_only_does_not_require_approval` |
| no approval | `test_an_unapproved_irreversible_action_is_refused` |
| changed proposal / digest mismatch | `test_editing_a_proposal_after_approval_invalidates_it` |
| expired approval | `test_an_expired_approval_is_refused` |
| replay / already acted | `test_an_action_cannot_be_replayed` |
| allowed once | `test_an_approved_action_proceeds` |
| named approver required | `test_an_approval_must_name_a_person` |

CircleCI additionally compiles `src/`, runs the walkthrough, and verifies that the public documentation and provenance files are present.
