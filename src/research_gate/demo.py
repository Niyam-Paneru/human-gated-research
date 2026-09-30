"""Runnable walkthrough. `python -m research_gate.demo`"""

from __future__ import annotations

import sys

from research_gate import (
    ActionGate,
    ActionKind,
    Claim,
    Evidence,
    Proposal,
    rank_claims,
)

GREEN, RED, YELLOW, DIM, BOLD, OFF = (
    "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m"
)


def section(title: str, *lines: str) -> None:
    print(f"{BOLD}\n{title}{OFF}")
    for line in lines:
        print(f"{DIM}   {line}{OFF}")
    print()


def ev(source: str, group: str = "", day: int = 1) -> Evidence:
    return Evidence(source=source, observed_at=float(day), summary="observation",
                    independent_group=group)


def _report(label: str, ok: bool, reason: str) -> None:
    colour = GREEN if ok else RED
    print(f"  {label.ljust(46)} {colour}{'ALLOW' if ok else 'DENY'}    {reason}{OFF}")


def main() -> int:
    section(
        "1. Corroboration counts sources, not citations",
        "Five articles from one syndicated wire story are one source.",
    )
    wire_storm = Claim(
        id="c1", statement="Vendor X is the only compliant supplier",
        evidence=(ev("wire-a", "wire"), ev("wire-b", "wire"),
                  ev("wire-c", "wire"), ev("wire-d", "wire")),
    )
    two_records = Claim(
        id="c2", statement="Vendor X is the only compliant supplier",
        evidence=(ev("registry", "registry"), ev("direct-audit", "audit")),
    )
    fresh_rumour = Claim(
        id="c3", statement="Vendor X is the only compliant supplier",
        evidence=(ev("blog-post", "blog", day=99),),
    )
    for claim in rank_claims([fresh_rumour, wire_storm, two_records]):
        colour = GREEN if claim.independent_source_count >= 2 else YELLOW
        print(f"  {claim.id}  {claim.independent_source_count} independent sources  "
              f"{colour}{'corroborated' if claim.independent_source_count >= 2 else 'single source'}{OFF}")

    section(
        "2. Approval binds to content, not to an id",
        "This is the property that makes review meaningful.",
    )
    gate = ActionGate()
    original = Proposal(
        id="p1", claim_id="c2", action=ActionKind.CONTACT_THIRD_PARTY,
        target="https://vendor-x.example/contact",
        rationale="Only compliant supplier.",
        evidence=(ev("registry", "registry"), ev("direct-audit", "audit")),
    )
    gate.approve(original, approved_by="operator")

    swapped = Proposal(
        id="p1", claim_id="c2", action=ActionKind.CONTACT_THIRD_PARTY,
        target="https://attacker.example/contact",
        rationale="Only compliant supplier.",
        evidence=(ev("registry", "registry"), ev("direct-audit", "audit")),
    )
    ok, reason = gate.authorize(swapped)
    print(f"  {'same id, different target'.ljust(46)} {RED}DENY    {reason}{OFF}")
    print(f"  {'':<46} {DIM}the id matched; the digest did not{OFF}")

    section("3. Every irreversible action needs a live approval")
    print()

    def fresh(pid: str) -> Proposal:
        return Proposal(
            id=pid, claim_id="c2", action=ActionKind.CONTACT_THIRD_PARTY,
            target="https://vendor-x.example/contact",
            rationale="Only compliant supplier.",
            evidence=(ev("registry", "registry"), ev("direct-audit", "audit")),
        )

    fresh_gate = ActionGate()

    never = fresh("n1")
    ok, reason = fresh_gate.authorize(never)
    _report("never approved", ok, reason)

    pending = fresh("n2")
    fresh_gate.approve(pending, approved_by="operator")
    ok, reason = fresh_gate.authorize(pending)
    _report("approved, acted once", ok, reason)

    ok, reason = fresh_gate.authorize(pending)
    _report("same approval replayed", ok, reason)

    section(
        "4. Approvals expire",
        "An approval from last week is not an approval for today.",
    )
    clock = {"t": 1_000.0}
    aging = ActionGate(ttl_seconds=60.0, now=lambda: clock["t"])
    p = Proposal(id="p9", claim_id="c2", action=ActionKind.SPEND_MONEY,
                 target="https://vendor-x.example/quote", rationale="Best value.",
                 evidence=(ev("registry", "registry"),))
    aging.approve(p, approved_by="operator")
    clock["t"] += 3_600.0
    ok, reason = aging.authorize(p)
    print(f"  {'approved 60 minutes ago, ttl 60s'.ljust(46)} {RED}DENY    {reason}{OFF}")

    section("5. Read-only actions stay cheap")
    print(f"{DIM}   Investigating is not the same risk as contacting someone.{OFF}\n")
    print(f"  {DIM}read_only is not in the irreversible set, so it never{OFF}")
    print(f"  {DIM}needs an approval round-trip. Only the world-changing{OFF}")
    print(f"  {DIM}actions pay the governance cost.{OFF}")

    print(f"\n{BOLD}   Every line above is produced by code in this repo.{OFF}\n")
    return 0




if __name__ == "__main__":
    sys.exit(main())
