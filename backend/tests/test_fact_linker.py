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


