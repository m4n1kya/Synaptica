"""
Unit tests for Synaptica LLM fact extraction parsing and safety utilities.
"""
import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fact_extractor import (
    _parse_json,
    _safe_response_text,
    extract_all_facts,
    extract_facts_from_chunk,
)
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


def test_extract_facts_from_chunk_no_api_key():
    """Verify extract_facts_from_chunk returns empty list when API key is missing."""
    chunk = {"text": "A" * 100, "page_numbers": [1]}
    with patch.dict("os.environ", {}, clear=True):
        facts = asyncio.run(extract_facts_from_chunk(chunk, "doc1", "doc1.pdf", api_key=""))
    assert facts == []


def test_extract_facts_from_chunk_short_text():
    """Verify extract_facts_from_chunk skips chunks shorter than 50 characters."""
    chunk = {"text": "Too short text", "page_numbers": [1]}
    facts = asyncio.run(extract_facts_from_chunk(chunk, "doc1", "doc1.pdf", api_key="valid_key"))
    assert facts == []


def test_extract_facts_from_chunk_success_mock():
    """Verify extract_facts_from_chunk parses structured facts and context correctly."""
    chunk = {
        "text": "Gross domestic product accelerated to 8.2% during FY2024-25 driven by manufacturing.",
        "page_numbers": [1]
    }

    mock_part = MagicMock()
    mock_part.text = json.dumps([
        {
            "statement": "GDP grew by 8.2% in FY2024-25",
            "value": "8.2",
            "unit": "%",
            "category": "GDP Growth",
            "confidence": 0.95,
            "evidence_text": "Gross domestic product accelerated to 8.2%",
            "page_numbers": [1],
            "context": {
                "time_period": "FY2024-25",
                "scope": "National",
                "methodology": "National Accounts"
            }
        }
    ])
    mock_candidate = MagicMock()
    mock_candidate.finish_reason = "STOP"
    mock_candidate.content.parts = [mock_part]

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("google.genai.Client", return_value=mock_client):
        facts = asyncio.run(extract_facts_from_chunk(chunk, "doc1", "doc1.pdf", api_key="dummy_key"))

    assert len(facts) == 1
    f = facts[0]
    assert f.statement == "GDP grew by 8.2% in FY2024-25"
    assert f.value == "8.2"
    assert f.unit == "%"
    assert f.category == "GDP Growth"
    assert f.confidence == 0.95
    assert f.context.time_period == "FY2024-25"
    assert f.context.scope == "National"


def test_extract_facts_from_chunk_json_decode_error():
    """Verify extract_facts_from_chunk returns empty list on invalid JSON response."""
    chunk = {"text": "A" * 100, "page_numbers": [1]}

    mock_part = MagicMock()
    mock_part.text = "This is not valid JSON content"
    mock_candidate = MagicMock()
    mock_candidate.finish_reason = "STOP"
    mock_candidate.content.parts = [mock_part]

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("google.genai.Client", return_value=mock_client):
        facts = asyncio.run(extract_facts_from_chunk(chunk, "doc1", "doc1.pdf", api_key="dummy_key"))

    assert facts == []


def test_extract_facts_from_chunk_general_exception():
    """Verify extract_facts_from_chunk returns empty list on unexpected exception."""
    chunk = {"text": "A" * 100, "page_numbers": [1]}

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(side_effect=RuntimeError("Unexpected client error"))

    with patch("google.genai.Client", return_value=mock_client):
        facts = asyncio.run(extract_facts_from_chunk(chunk, "doc1", "doc1.pdf", api_key="dummy_key"))

    assert facts == []


def test_safe_response_text_fallback_to_text():
    """Verify fallback to response.text when candidate content parts are absent."""
    mock_candidate = MagicMock()
    mock_candidate.finish_reason = "STOP"
    mock_candidate.content.parts = []

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]
    mock_response.text = '[{"statement": "Direct text fallback", "value": "100"}]'

    text = _safe_response_text(mock_response)
    assert text == '[{"statement": "Direct text fallback", "value": "100"}]'


def test_safe_response_text_exception_handled():
    """Verify exceptions during response text extraction return None without crashing."""
    mock_response = MagicMock()
    # Accessing candidates raises an unhandled RuntimeError
    type(mock_response).candidates = property(lambda self: (_ for _ in ()).throw(RuntimeError("Broken candidate access")))

    text = _safe_response_text(mock_response)
    assert text is None


def test_extract_facts_from_chunk_malformed_context_and_empty_statement():
    """Verify extract_facts_from_chunk handles non-dict context and skips facts without statement."""
    chunk = {"text": "Gross domestic product accelerated to 8.2% during FY24.", "page_numbers": [2]}

    mock_part = MagicMock()
    mock_part.text = json.dumps([
        {
            "statement": "",  # Empty statement, should be skipped
            "value": "100",
        },
        {
            "statement": "Real GDP grew by 8.2%",
            "value": "8.2",
            "context": "Not a dictionary object",  # Malformed context, should fallback to empty Context
        }
    ])
    mock_candidate = MagicMock()
    mock_candidate.finish_reason = "STOP"
    mock_candidate.content.parts = [mock_part]

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch("google.genai.Client", return_value=mock_client):
        facts = asyncio.run(extract_facts_from_chunk(chunk, "doc1", "doc1.pdf", api_key="dummy_key"))

    assert len(facts) == 1
    assert facts[0].statement == "Real GDP grew by 8.2%"
    assert facts[0].context.time_period == ""


def test_extract_facts_from_chunk_rate_limit_retry_success():
    """Verify extract_facts_from_chunk retries with exponential backoff on 429 / RESOURCE_EXHAUSTED."""
    chunk = {"text": "A" * 100, "page_numbers": [1]}

    mock_part = MagicMock()
    mock_part.text = json.dumps([{"statement": "Retried successfully", "value": "10"}])
    mock_candidate = MagicMock()
    mock_candidate.finish_reason = "STOP"
    mock_candidate.content.parts = [mock_part]

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    mock_client = MagicMock()
    # First call raises 429 quota error; second call succeeds
    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=[Exception("429 RESOURCE_EXHAUSTED: quota exceeded"), mock_response]
    )

    with patch("google.genai.Client", return_value=mock_client), patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        facts = asyncio.run(extract_facts_from_chunk(chunk, "doc1", "doc1.pdf", api_key="dummy_key"))

    assert len(facts) == 1
    assert facts[0].statement == "Retried successfully"
    assert mock_sleep.call_count == 1
    # First attempt wait should be 10 seconds: (2 ** 0) * 10
    assert mock_sleep.call_args[0][0] == 10


def test_extract_facts_from_chunk_all_retries_fail():
    """Verify extract_facts_from_chunk returns empty list when all 3 attempts hit rate limits."""
    chunk = {"text": "A" * 100, "page_numbers": [1]}

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=Exception("503 Service UNAVAILABLE")
    )

    with patch("google.genai.Client", return_value=mock_client), patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        facts = asyncio.run(extract_facts_from_chunk(chunk, "doc1", "doc1.pdf", api_key="dummy_key"))

    assert facts == []
    assert mock_sleep.call_count == 3



