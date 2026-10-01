import pytest

from research_gate import Claim, Evidence, rank_claims


def ev(source: str, group: str = "", day: int = 1) -> Evidence:
    return Evidence(source=source, observed_at=float(day), summary="observed", independent_group=group)


def test_source_is_required():
    with pytest.raises(ValueError):
        Evidence(source=" ", observed_at=1.0, summary="trust me")


def test_independent_groups_not_raw_citation_count():
    claim = Claim(
        id="c",
        statement="x",
        evidence=(ev("wire-a", "wire"), ev("wire-b", "wire"), ev("registry", "registry")),
    )
    assert claim.independent_source_count == 2


def test_corroboration_beats_single_fresh_source():
    strong = Claim(id="a", statement="a", evidence=(ev("s1", "g1"), ev("s2", "g2")))
    fresh = Claim(id="b", statement="b", evidence=(ev("blog", day=99),))
    assert rank_claims([fresh, strong])[0].id == "a"
