"""
Unit tests for Synaptica LLM fact extraction parsing and safety utilities.
"""
import asyncio
import json
import pytest
from unittest.mock import MagicMock, patch
from fact_extractor import _parse_json, _safe_response_text, extract_all_facts
from models import Fact


def test_parse_json_clean_array():
    """Verify parsing a clean JSON array string."""
    raw = '[{"statement": "GDP grew by 8.2%", "value": "8.2", "confidence": 0.9}]'
    result = _parse_json(raw)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["value"] == "8.2"


def test_parse_json_markdown_fences():
    """Verify stripping markdown code fences commonly output by LLMs."""
    raw = """```json
    [
      {"statement": "Inflation at 4.5%", "value": "4.5", "confidence": 0.85}
    ]
    ```"""
    result = _parse_json(raw)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["statement"] == "Inflation at 4.5%"


def test_parse_json_with_surrounding_text():
    """Verify extracting the array when conversational text surrounds the JSON."""
    raw = """Here is the extracted information:
    [
      {"statement": "Revenue increased 45%", "value": "45"}
    ]
    I hope this helps!"""
    result = _parse_json(raw)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["value"] == "45"


def test_parse_json_empty_array():
    """Verify parsing an empty array string."""
    assert _parse_json("[]") == []
    assert _parse_json("   []   ") == []


def test_parse_json_invalid_syntax():
    """Verify invalid JSON syntax raises a JSONDecodeError."""
    with pytest.raises(json.JSONDecodeError):
        _parse_json("[invalid json")


def test_safe_response_text_normal():
    """Verify text extraction from standard candidate parts."""
    mock_part = MagicMock()
    mock_part.text = "Sample extracted content"
    mock_candidate = MagicMock()
    mock_candidate.finish_reason = "STOP"
    mock_candidate.content.parts = [mock_part]

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    text = _safe_response_text(mock_response)
    assert text == "Sample extracted content"


def test_safe_response_text_empty_candidates():
    """Verify handling when response has empty candidates."""
    mock_response = MagicMock()
    mock_response.candidates = []
    assert _safe_response_text(mock_response) is None


def test_safe_response_text_safety_block():
    """Verify safety block finish reasons return None."""
    mock_candidate = MagicMock()
    mock_candidate.finish_reason = "SAFETY"

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    assert _safe_response_text(mock_response) is None


def test_extract_all_facts_empty_chunks():
    """Verify extract_all_facts handles empty chunks without error."""
    result = asyncio.run(extract_all_facts([], "doc_123", "sample.pdf"))
    assert result == []


def test_extract_all_facts_deduplication():
    """Verify extract_all_facts eliminates duplicate statements across chunks."""
    f1 = Fact(id="f1", statement="Headline CPI reached 4.5%", category="Inflation", source_doc_id="doc_1")
    f2 = Fact(id="f2", statement="headline cpi reached 4.5%  ", category="Inflation", source_doc_id="doc_1")
    f3 = Fact(id="f3", statement="GDP growth projected at 7.0%", category="Macroeconomics", source_doc_id="doc_1")

    # Mock extract_facts_from_chunk to return f1 on first chunk, f2 and f3 on second chunk
    chunks = [{"page_numbers": [1], "text": "text1"}, {"page_numbers": [2], "text": "text2"}]

    with patch("fact_extractor.extract_facts_from_chunk") as mock_extract:
        mock_extract.side_effect = [[f1], [f2, f3]]
        unique_facts = asyncio.run(extract_all_facts(chunks, "doc_1", "sample.pdf", api_key="dummy_key"))

    assert len(unique_facts) == 2
    assert unique_facts[0].id == "f1"
    assert unique_facts[1].id == "f3"

