# Design overview

Research and external action are treated as different capabilities.

The public flow is:

**evidence → claim ranking → proposal → human approval → digest check → action authorization**

The digest is the important seam.

An approval is tied to the exact proposal content a person reviewed. Reusing the same proposal id after changing the target or rationale does not inherit the old approval.

The code is split into evidence ranking, canonical digests, proposal serialization, and the action gate so each part can be inspected separately.
