"""
Unit tests for Synaptica fact linking and candidate pair generation logic.
"""
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from models import Fact, Relationship
from fact_linker import (
    find_candidate_pairs,
    find_candidate_pairs_incremental,
    classify_relationship,
    link_all_facts,
    link_incremental,
    get_canonical_pair_key,
    filter_relationships_by_threshold,
    get_conflicting_relationships,
    group_relationships_by_type,
)


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


def test_classify_relationship_missing_api_key():
    """Verify classify_relationship returns None when no API key is provided."""
    fact_a = Fact(id="fa", statement="Statement A", category="Cat", source_doc_id="d1")
    fact_b = Fact(id="fb", statement="Statement B", category="Cat", source_doc_id="d2")
    with patch.dict("os.environ", {}, clear=True):
        res = asyncio.run(classify_relationship(fact_a, fact_b, api_key=""))
    assert res is None


def test_classify_relationship_corroborates_success():
    """Verify classify_relationship correctly creates a Relationship model when LLM detects corroboration."""
    fact_a = Fact(id="fa", statement="Inflation reached 4.5%", category="Inflation", source_doc_id="d1")
    fact_b = Fact(id="fb", statement="CPI printed 4.5%", category="Inflation", source_doc_id="d2")

    mock_response = MagicMock()
    mock_response.text = '{"relationship_type": "corroborates", "explanation": "Identical metrics", "confidence": 0.95}'

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("google.genai.Client", return_value=mock_client):
        result = asyncio.run(classify_relationship(fact_a, fact_b, api_key="mock_key"))

    assert result is not None
    assert isinstance(result, Relationship)
    assert result.relationship_type == "corroborates"
    assert result.fact_a_id == "fa"
    assert result.fact_b_id == "fb"
    assert result.confidence == 0.95
    assert result.explanation == "Identical metrics"


def test_classify_relationship_unrelated_returns_none():
    """Verify classify_relationship returns None when relationship_type is unrelated."""
    fact_a = Fact(id="fa", statement="Tax revenue surged", category="Fiscal", source_doc_id="d1")
    fact_b = Fact(id="fb", statement="Literacy rate increased", category="Social", source_doc_id="d2")

    mock_response = MagicMock()
    mock_response.text = '{"relationship_type": "unrelated", "explanation": "Different domains"}'

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("google.genai.Client", return_value=mock_client):
        result = asyncio.run(classify_relationship(fact_a, fact_b, api_key="mock_key"))

    assert result is None


def test_classify_relationship_with_markdown_fences():
    """Verify classify_relationship strips markdown fences from LLM responses."""
    fact_a = Fact(id="fa", statement="Deficit at 5.1%", category="Fiscal", source_doc_id="d1")
    fact_b = Fact(id="fb", statement="Deficit estimated at 5.8%", category="Fiscal", source_doc_id="d2")

    mock_response = MagicMock()
    mock_response.text = """```json
    {
      "relationship_type": "contradicts",
      "explanation": "Conflicting fiscal deficit estimates for same period",
      "confidence": 0.88
    }
    ```"""

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("google.genai.Client", return_value=mock_client):
        result = asyncio.run(classify_relationship(fact_a, fact_b, api_key="mock_key"))

    assert result is not None
    assert result.relationship_type == "contradicts"
    assert result.confidence == 0.88


def test_classify_relationship_api_error_returns_none():
    """Verify classify_relationship catches API exceptions and returns None gracefully."""
    fact_a = Fact(id="fa", statement="Fact A", category="Cat", source_doc_id="d1")
    fact_b = Fact(id="fb", statement="Fact B", category="Cat", source_doc_id="d2")

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(side_effect=Exception("Gemini quota exceeded"))

    with patch("google.genai.Client", return_value=mock_client):
        result = asyncio.run(classify_relationship(fact_a, fact_b, api_key="mock_key"))

    assert result is None


def test_link_all_facts_empty():
    """Verify link_all_facts returns empty list for empty facts input."""
    result = asyncio.run(link_all_facts([], api_key="dummy_key"))
    assert result == []


def test_link_all_facts_concurrent_mock():
    """Verify link_all_facts concurrently resolves candidate pairs into relationships."""
    fact_a = Fact(id="fa", statement="Fact A", category="Shared", source_doc_id="d1")
    fact_b = Fact(id="fb", statement="Fact B", category="Shared", source_doc_id="d2")
    rel = Relationship(
        id="rel-1",
        fact_a_id="fa",
        fact_b_id="fb",
        relationship_type="corroborates",
        explanation="Consistent",
        confidence=0.9
    )

    with patch("fact_linker.classify_relationship", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = rel
        relationships = asyncio.run(link_all_facts([fact_a, fact_b], api_key="mock_key"))

    assert len(relationships) == 1
    assert relationships[0].id == "rel-1"


def test_link_incremental_empty_inputs():
    """Verify link_incremental returns empty list when either fact list is empty."""
    fact = Fact(id="f1", statement="Revenue grew", category="Revenue", source_doc_id="d1")
    assert asyncio.run(link_incremental([], [fact], api_key="dummy_key")) == []
    assert asyncio.run(link_incremental([fact], [], api_key="dummy_key")) == []
    assert asyncio.run(link_incremental([], [], api_key="dummy_key")) == []


def test_link_incremental_concurrent_mock():
    """Verify link_incremental pairs new facts with existing facts and gathers relationships."""
    new_fact = Fact(id="nf1", statement="New revenue data", category="Revenue", source_doc_id="d_new")
    existing_fact = Fact(id="ef1", statement="Old revenue data", category="Revenue", source_doc_id="d_old")
    rel = Relationship(
        id="rel-inc-1",
        fact_a_id="nf1",
        fact_b_id="ef1",
        relationship_type="corroborates",
        explanation="Both state strong revenue numbers",
        confidence=0.92
    )

    with patch("fact_linker.classify_relationship", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = rel
        relationships = asyncio.run(link_incremental([new_fact], [existing_fact], api_key="mock_key"))

    assert len(relationships) == 1
    assert relationships[0].id == "rel-inc-1"


def test_link_all_facts_exception_handled():
    """Verify link_all_facts gracefully logs exceptions from individual pair tasks without crashing."""
    fact_a = Fact(id="fa", statement="Statement A", category="General", source_doc_id="doc1")
    fact_b = Fact(id="fb", statement="Statement B", category="General", source_doc_id="doc2")

    with patch("fact_linker.classify_relationship", new_callable=AsyncMock) as mock_classify:
        mock_classify.side_effect = RuntimeError("Pair analysis network failure")
        relationships = asyncio.run(link_all_facts([fact_a, fact_b], api_key="test_key"))

    assert relationships == []


def test_link_incremental_exception_handled():
    """Verify link_incremental catches and handles task exceptions gracefully."""
    new_fact = Fact(id="nf", statement="New fact", category="General", source_doc_id="doc_new")
    existing_fact = Fact(id="ef", statement="Existing fact", category="General", source_doc_id="doc_old")

    with patch("fact_linker.classify_relationship", new_callable=AsyncMock) as mock_classify:
        mock_classify.side_effect = TimeoutError("Classification timeout")
        relationships = asyncio.run(link_incremental([new_fact], [existing_fact], api_key="test_key"))

    assert relationships == []


def test_get_canonical_pair_key():
    """Verify get_canonical_pair_key produces deterministic order-independent keys."""
    f1 = Fact(id="fact_001", statement="S1")
    f2 = Fact(id="fact_002", statement="S2")

    key1 = get_canonical_pair_key(f1, f2)
    key2 = get_canonical_pair_key(f2, f1)

    assert key1 == ("fact_001", "fact_002")
    assert key1 == key2


def test_filter_relationships_by_threshold():
    """Verify filter_relationships_by_threshold filters correctly by confidence."""
    r_high = Relationship(id="r1", fact_a_id="a", fact_b_id="b", relationship_type="corroborates", confidence=0.85)
    r_mid = Relationship(id="r2", fact_a_id="a", fact_b_id="c", relationship_type="contradicts", confidence=0.60)
    r_low = Relationship(id="r3", fact_a_id="b", fact_b_id="c", relationship_type="contextual_difference", confidence=0.35)

    filtered = filter_relationships_by_threshold([r_high, r_mid, r_low], min_confidence=0.5)
    assert len(filtered) == 2
    assert [r.id for r in filtered] == ["r1", "r2"]

    strict = filter_relationships_by_threshold([r_high, r_mid, r_low], min_confidence=0.8)
    assert len(strict) == 1
    assert strict[0].id == "r1"


def test_get_conflicting_relationships_and_grouping():
    """Verify get_conflicting_relationships and group_relationships_by_type utilities."""
    r_corrob = Relationship(id="r1", fact_a_id="a", fact_b_id="b", relationship_type="corroborates", confidence=0.9)
    r_contra = Relationship(id="r2", fact_a_id="a", fact_b_id="c", relationship_type="contradicts", confidence=0.8)
    r_context = Relationship(id="r3", fact_a_id="b", fact_b_id="d", relationship_type="contextual_difference", confidence=0.85)

    all_rels = [r_corrob, r_contra, r_context]

    conflicts = get_conflicting_relationships(all_rels)
    assert len(conflicts) == 2
    assert r_contra in conflicts
    assert r_context in conflicts
    assert r_corrob not in conflicts

    grouped = group_relationships_by_type(all_rels)
    assert len(grouped["corroborates"]) == 1
    assert len(grouped["contradicts"]) == 1
    assert len(grouped["contextual_difference"]) == 1
    assert grouped["corroborates"][0].id == "r1"






