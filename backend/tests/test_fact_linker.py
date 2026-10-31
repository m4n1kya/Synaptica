"""
Unit tests for Synaptica fact linking and candidate pair generation logic.
"""
from models import Fact
from fact_linker import find_candidate_pairs, find_candidate_pairs_incremental


def test_find_candidate_pairs_same_category():
    """Verify facts in the same category from different documents are paired."""
    fact_a = Fact(
        id="fact_a",
        statement="GDP grew by 8.2%",
        value="8.2",
        unit="%",
        category="Macroeconomics",
        source_doc_id="doc_1",
    )
    fact_b = Fact(
        id="fact_b",
        statement="Real GDP expansion reached 7.8%",
        value="7.8",
        unit="%",
        category="Macroeconomics",
        source_doc_id="doc_2",
    )
    pairs = find_candidate_pairs([fact_a, fact_b])
    assert len(pairs) == 1
    assert pairs[0] == (fact_a, fact_b)


def test_find_candidate_pairs_same_value_and_unit():
    """Verify facts with matching values and units are paired across categories."""
    fact_a = Fact(
        id="fact_a",
        statement="Revenue reached 500 crore",
        value="500",
        unit="crore",
        category="Revenue",
        source_doc_id="doc_1",
    )
    fact_b = Fact(
        id="fact_b",
        statement="Market cap valuation reported at 500 crore",
        value="500",
        unit="crore",
        category="Capital Markets",
        source_doc_id="doc_2",
    )
    pairs = find_candidate_pairs([fact_a, fact_b])
    assert len(pairs) == 1
    assert pairs[0] == (fact_a, fact_b)


def test_find_candidate_pairs_same_document_ignored():
    """Ensure facts from the same document are never paired together."""
    fact_a = Fact(
        id="fact_a",
        statement="Statement 1",
        category="Operations",
        source_doc_id="doc_1",
    )
    fact_b = Fact(
        id="fact_b",
        statement="Statement 2",
        category="Operations",
        source_doc_id="doc_1",
    )
    pairs = find_candidate_pairs([fact_a, fact_b])
    assert len(pairs) == 0


def test_find_candidate_pairs_no_match():
    """Ensure unrelated facts with different categories and values are not paired."""
    fact_a = Fact(
        id="fact_a",
        statement="Workforce of 50,000 employees",
        value="50000",
        unit="employees",
        category="Workforce",
        source_doc_id="doc_1",
    )
    fact_b = Fact(
        id="fact_b",
        statement="Headline CPI inflation at 4.5%",
        value="4.5",
        unit="%",
        category="Inflation",
        source_doc_id="doc_2",
    )
    pairs = find_candidate_pairs([fact_a, fact_b])
    assert len(pairs) == 0


def test_find_candidate_pairs_no_duplicates():
    """Verify pairing does not produce symmetric duplicates."""
    facts = [
        Fact(id=f"f{i}", statement=f"Fact {i}", category="Trade", source_doc_id=f"doc_{i}")
        for i in range(4)
    ]
    pairs = find_candidate_pairs(facts)
    # 4 distinct docs in same category = 4 * 3 / 2 = 6 pairs
    assert len(pairs) == 6
    # Ensure no duplicates or flipped pairs
    seen = set()
    for fa, fb in pairs:
        pair_key = tuple(sorted([fa.id, fb.id]))
        assert pair_key not in seen
        seen.add(pair_key)


def test_find_candidate_pairs_empty():
    """Verify empty input returns empty list."""
    assert find_candidate_pairs([]) == []


def test_find_candidate_pairs_incremental_matching_category():
    """Verify incremental linking pairs new facts with existing facts in the same category."""
    new_fact = Fact(id="nf1", statement="New revenue data", category="Revenue", source_doc_id="doc_new")
    existing_fact1 = Fact(id="ef1", statement="Past revenue data", category="Revenue", source_doc_id="doc_old")
    existing_fact2 = Fact(id="ef2", statement="Inflation rate", category="Inflation", source_doc_id="doc_old")

    pairs = find_candidate_pairs_incremental([new_fact], [existing_fact1, existing_fact2])
    assert len(pairs) == 1
    assert pairs[0] == (new_fact, existing_fact1)


def test_find_candidate_pairs_incremental_matching_value():
    """Verify incremental linking pairs new facts with existing facts sharing value & unit."""
    new_fact = Fact(
        id="nf1",
        statement="New company metric",
        value="12.5",
        unit="%",
        category="Operations",
        source_doc_id="doc_new",
    )
    existing_fact = Fact(
        id="ef1",
        statement="Prior metric",
        value="12.5",
        unit="%",
        category="Profitability",
        source_doc_id="doc_old",
    )

    pairs = find_candidate_pairs_incremental([new_fact], [existing_fact])
    assert len(pairs) == 1
    assert pairs[0] == (new_fact, existing_fact)


def test_find_candidate_pairs_incremental_same_doc_excluded():
    """Verify incremental linking ignores facts originating from the same document."""
    new_fact = Fact(id="nf1", statement="Claim A", category="Trade", source_doc_id="doc_shared")
    existing_fact = Fact(id="ef1", statement="Claim B", category="Trade", source_doc_id="doc_shared")

    pairs = find_candidate_pairs_incremental([new_fact], [existing_fact])
    assert len(pairs) == 0


def test_find_candidate_pairs_incremental_empty_inputs():
    """Verify incremental pairing returns empty list when either input is empty."""
    fact = Fact(id="f1", statement="Claim", category="Trade", source_doc_id="doc_1")
    assert find_candidate_pairs_incremental([], [fact]) == []
    assert find_candidate_pairs_incremental([fact], []) == []
    assert find_candidate_pairs_incremental([], []) == []

