"""
Unit tests for Synaptica PDF processing and sliding-window chunking utilities.
"""
from pdf_processor import (
    PageContent,
    DocumentContent,
    _is_numeric_token,
    _detect_table_pattern,
    chunk_pages,
)


def test_is_numeric_token():
    """Verify numeric token detector handles various formatting and currency symbols."""
    # Standard numbers
    assert _is_numeric_token("100") is True
    assert _is_numeric_token("3.14") is True
    assert _is_numeric_token("-42") is True

    # Formatted financial numbers
    assert _is_numeric_token("1,089") is True
    assert _is_numeric_token("8.2%") is True
    assert _is_numeric_token("₹500") is True
    assert _is_numeric_token("-0.5%") is True

    # Non-numeric tokens
    assert _is_numeric_token("GDP") is False
    assert _is_numeric_token("growth") is False
    assert _is_numeric_token("FY2024-25") is False
    assert _is_numeric_token("") is False


def test_detect_table_pattern_positive():
    """Verify table pattern detection on multiline tabular numeric rows."""
    tabular_text = """
    Year      Actuals    Budget     Revised
    2022-23   1200       1350       1290
    2023-24   1450       1500       1480
    2024-25   1600       1750       1720
    """
    assert _detect_table_pattern(tabular_text) is True


def test_detect_table_pattern_negative():
    """Verify table pattern detection correctly ignores prose paragraphs."""
    prose_text = """
    India's economy continues to show resilience amidst global macroeconomic headwinds.
    Domestic consumption remained a primary driver of overall output.
    Inflationary pressures were largely moderated by proactive monetary policy.
    """
    assert _detect_table_pattern(prose_text) is False


def test_chunk_pages_sliding_window():
    """Verify that pages are grouped into overlapping sliding-window chunks."""
    pages = [
        PageContent(page_number=1, text="Content of page 1", char_count=17),
        PageContent(page_number=2, text="Content of page 2 with table", char_count=28, has_tables=True),
        PageContent(page_number=3, text="Content of page 3", char_count=17),
        PageContent(page_number=4, text="Content of page 4", char_count=17),
        PageContent(page_number=5, text="Content of page 5", char_count=17),
    ]
    doc = DocumentContent(filename="sample.pdf", total_pages=5, pages=pages)

    # Chunk size of 3 with step (chunk_size - 1) = 2 (1-page overlap)
    chunks = chunk_pages(doc, chunk_size=3)

    assert len(chunks) == 3
    # Chunk 1: pages 1, 2, 3
    assert chunks[0]["page_numbers"] == [1, 2, 3]
    assert chunks[0]["has_tables"] is True
    assert "--- Page 1 ---" in chunks[0]["text"]
    assert "--- Page 2 ---" in chunks[0]["text"]
    assert "--- Page 3 ---" in chunks[0]["text"]

    # Chunk 2: pages 3, 4, 5 (overlaps page 3)
    assert chunks[1]["page_numbers"] == [3, 4, 5]
    assert chunks[1]["has_tables"] is False

    # Chunk 3: page 5 (trailing remainder)
    assert chunks[2]["page_numbers"] == [5]


def test_chunk_pages_empty_document():
    """Verify chunk_pages handles empty document cleanly."""
    doc = DocumentContent(filename="empty.pdf", total_pages=0, pages=[])
    chunks = chunk_pages(doc, chunk_size=3)
    assert chunks == []
