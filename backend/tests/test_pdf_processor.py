"""
Unit tests for Synaptica PDF processing and sliding-window chunking utilities.
"""
from unittest.mock import MagicMock, patch
from pdf_processor import (
    PageContent,
    DocumentContent,
    _is_numeric_token,
    _detect_table_pattern,
    chunk_pages,
    extract_pdf_text,
    format_pdf_date,
)


def test_is_numeric_token():
    """Verify numeric token detector handles various formatting, currencies, and financial notation."""
    # Standard numbers
    assert _is_numeric_token("100") is True
    assert _is_numeric_token("3.14") is True
    assert _is_numeric_token("-42") is True
    assert _is_numeric_token("+15.8") is True

    # Formatted financial numbers and global currencies
    assert _is_numeric_token("1,089") is True
    assert _is_numeric_token("8.2%") is True
    assert _is_numeric_token("₹500") is True
    assert _is_numeric_token("$1,250.50") is True
    assert _is_numeric_token("€450") is True
    assert _is_numeric_token("£95.20") is True
    assert _is_numeric_token("¥10,000") is True
    assert _is_numeric_token("-0.5%") is True

    # Accounting negative notation in parentheses
    assert _is_numeric_token("(450.25)") is True
    assert _is_numeric_token("(1,200)") is True

    # Financial magnitude suffixes (South Asian and International)
    assert _is_numeric_token("12.5bn") is True
    assert _is_numeric_token("300cr") is True
    assert _is_numeric_token("50lakh") is True
    assert _is_numeric_token("25bps") is True
    assert _is_numeric_token("14.5x") is True
    assert _is_numeric_token("500M") is True
    assert _is_numeric_token("250k") is True

    # Non-numeric tokens
    assert _is_numeric_token("GDP") is False
    assert _is_numeric_token("growth") is False
    assert _is_numeric_token("FY2024-25") is False
    assert _is_numeric_token("") is False
    assert _is_numeric_token("   ") is False


def test_detect_table_pattern_positive():
    """Verify table pattern detection on multiline tabular numeric rows."""
    tabular_text = """
    Year      Actuals    Budget     Revised
    2022-23   1200       1350       1290
    2023-24   1450       1500       1480
    2024-25   1600       1750       1720
    """
    assert _detect_table_pattern(tabular_text) is True


def test_detect_table_pattern_financial_mix():
    """Verify table pattern detection with mixed financial figures and currencies."""
    financial_table = """
    Metric          FY22        FY23        FY24
    Revenue         $1,200M     $1,450M     $1,800M
    EBITDA          $250M       $320M       $410M
    PAT Margin      12.5%       14.2%       16.0%
    """
    assert _detect_table_pattern(financial_table) is True


def test_detect_table_pattern_short_text():
    """Verify table pattern detection returns False for text with fewer than 3 lines."""
    assert _detect_table_pattern("Single line of text") is False
    assert _detect_table_pattern("Line 1\nLine 2") is False


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


def test_chunk_pages_single_page_chunk_size():
    """Verify chunk_pages handles chunk_size of 1 without division/zero-step error."""
    pages = [
        PageContent(page_number=1, text="Page 1 text", char_count=11),
        PageContent(page_number=2, text="Page 2 text", char_count=11),
    ]
    doc = DocumentContent(filename="sample2.pdf", total_pages=2, pages=pages)
    chunks = chunk_pages(doc, chunk_size=1)
    assert len(chunks) == 2
    assert chunks[0]["page_numbers"] == [1]
    assert chunks[1]["page_numbers"] == [2]


def test_extract_pdf_text_missing_file():
    """Verify extract_pdf_text returns None when target file does not exist."""
    result = extract_pdf_text("non_existent_document_404.pdf")
    assert result is None


def test_extract_pdf_text_successful_mock():
    """Verify extract_pdf_text correctly parses pages, metadata, tables, and images."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Col1\tCol2\tCol3\tCol4\tCol5\tCol6\tCol7"
    mock_page.images = [MagicMock()]

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_reader.metadata = {
        "/Title": "Annual Fiscal Policy",
        "/Author": "Ministry of Finance",
        "/Subject": "Macroeconomics",
        "/Creator": "ReportEngine",
    }

    with patch("os.path.exists", return_value=True), patch("pypdf.PdfReader", return_value=mock_reader):
        content = extract_pdf_text("mocked_annual_report.pdf")

    assert content is not None
    assert content.filename == "mocked_annual_report.pdf"
    assert content.total_pages == 1
    assert content.metadata["title"] == "Annual Fiscal Policy"
    assert content.metadata["author"] == "Ministry of Finance"
    assert len(content.pages) == 1
    page = content.pages[0]
    assert page.page_number == 1
    assert page.has_tables is True
    assert page.has_images is True


def test_extract_pdf_text_exception_handled():
    """Verify extract_pdf_text catches corrupt PDF read errors gracefully."""
    with patch("os.path.exists", return_value=True), patch("pypdf.PdfReader", side_effect=Exception("Corrupt PDF")):
        result = extract_pdf_text("corrupted_report.pdf")
    assert result is None


def test_extract_pdf_text_import_error():
    """Verify extract_pdf_text handles missing pypdf dependency gracefully."""
    with patch.dict("sys.modules", {"pypdf": None}):
        result = extract_pdf_text("sample.pdf")
    assert result is None


def test_document_content_word_and_char_aggregations():
    """Verify DocumentContent total_words and total_characters properties."""
    p1 = PageContent(page_number=1, text="India's economy is resilient", char_count=28, word_count=4)
    p2 = PageContent(page_number=2, text="Growth projected at 7%", char_count=22, word_count=4)
    doc = DocumentContent(filename="econ.pdf", total_pages=2, pages=[p1, p2])

    assert doc.total_words == 8
    assert doc.total_characters == 50

    chunks = chunk_pages(doc, chunk_size=2)
    assert len(chunks) == 2
    assert chunks[0]["word_count"] == 8
    assert chunks[1]["word_count"] == 4


def test_extract_pdf_text_dates_and_formatting():
    """Verify format_pdf_date parser and date metadata extraction in extract_pdf_text."""
    # Test date formatting helper directly
    assert format_pdf_date("D:20240315143000Z") == "2024-03-15"
    assert format_pdf_date("2023-11-20") == "2023-11-20"
    assert format_pdf_date("") == ""
    assert format_pdf_date(None) == ""

    # Test PDF extraction with creation and modification dates
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Page content without tables."
    mock_page.images = []

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_reader.metadata = {
        "/Title": "Fiscal Deficit Review",
        "/Author": "RBI",
        "/CreationDate": "D:20240210100000Z",
        "/ModDate": "D:20240212110000Z",
    }

    with patch("os.path.exists", return_value=True), patch("pypdf.PdfReader", return_value=mock_reader):
        content = extract_pdf_text("fiscal_review.pdf")

    assert content is not None
    assert content.metadata["title"] == "Fiscal Deficit Review"
    assert content.metadata["creation_date"] == "2024-02-10"
    assert content.metadata["modification_date"] == "2024-02-12"



