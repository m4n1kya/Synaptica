"""
Unit tests for Synaptica fact linking and candidate pair generation logic.
"""
from models import Fact
from fact_linker import find_candidate_pairs


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
