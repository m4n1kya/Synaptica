"""
Unit tests for Synaptica LLM fact extraction parsing and safety utilities.
"""
import json
import pytest
from unittest.mock import MagicMock
from fact_extractor import _parse_json, _safe_response_text


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
