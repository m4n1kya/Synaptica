"""
Synaptica — PDF Processor
Extracts text content from PDF files with page-level metadata using pypdf.
"""
import logging
import os
from typing import List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("synaptica.pdf_processor")


@dataclass
class PageContent:
    """Extracted content from a single PDF page."""
    page_number: int
    text: str
    char_count: int = 0
    word_count: int = 0
    has_tables: bool = False
    has_images: bool = False


@dataclass
class DocumentContent:
    """Complete extracted content from a PDF document."""
    filename: str
    total_pages: int
    pages: List[PageContent] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def total_words(self) -> int:
        """Sum of words across all extracted pages."""
        return sum(p.word_count for p in self.pages)

    @property
    def total_characters(self) -> int:
        """Sum of characters across all extracted pages."""
        return sum(p.char_count for p in self.pages)


def format_pdf_date(date_str: str) -> str:
    """Format PDF date string like 'D:20240115120000Z' into standard 'YYYY-MM-DD'."""
    if not date_str:
        return ""
    cleaned = date_str.strip()
    if cleaned.startswith("D:"):
        cleaned = cleaned[2:]
    if len(cleaned) >= 8 and cleaned[:8].isdigit():
        return f"{cleaned[:4]}-{cleaned[4:6]}-{cleaned[6:8]}"
    return cleaned


def extract_pdf_text(filepath: str) -> Optional[DocumentContent]:
    """
    Extract text from a PDF file using pypdf.
    Returns structured content with per-page text and metadata.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        logger.warning("pypdf not installed. Install with: pip install pypdf")
        return None

    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return None

    try:
        reader = PdfReader(filepath)
        meta = reader.metadata or {}
        raw_creation = str(meta.get("/CreationDate", "") or "")
        raw_mod = str(meta.get("/ModDate", "") or "")
        
        content = DocumentContent(
            filename=os.path.basename(filepath),
            total_pages=len(reader.pages),
            metadata={
                "title": meta.get("/Title", ""),
                "author": meta.get("/Author", ""),
                "subject": meta.get("/Subject", ""),
                "creator": meta.get("/Creator", ""),
                "creation_date": format_pdf_date(raw_creation),
                "modification_date": format_pdf_date(raw_mod),
            }
        )

        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            
            # Detect if page has tables (heuristic: multiple tab/aligned columns)
            has_tables = text.count("\t") > 5 or _detect_table_pattern(text)
            
            # Detect if page has images (pypdf has page.images)
            has_images = len(page.images) > 0 if hasattr(page, 'images') else False

            cleaned = text.strip()
            content.pages.append(PageContent(
                page_number=i + 1,  # 1-indexed
                text=cleaned,
                char_count=len(cleaned),
                word_count=len(cleaned.split()) if cleaned else 0,
                has_tables=has_tables,
                has_images=has_images
            ))

        return content

    except Exception as e:
        logger.error(f"Error processing PDF {filepath}: {e}")
        return None


def _detect_table_pattern(text: str) -> bool:
    """Heuristic to detect table-like patterns in extracted text."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if len(lines) < 3:
        return False
    # Count lines with multiple number-like tokens (suggests data rows)
    numeric_lines = 0
    for line in lines:
        tokens = line.split()
        num_count = sum(1 for t in tokens if _is_numeric_token(t))
        if num_count >= 3:
            numeric_lines += 1
    return numeric_lines >= 3


def _is_numeric_token(token: str) -> bool:
    """Check if a token looks like a number (including currency, accounting parentheses, and financial magnitudes)."""
    if not token:
        return False
    # Strip common enclosing punctuation (parentheses for negative financial figures, brackets, quotes)
    cleaned = token.strip(" \t\n\r()[]\"'")
    if not cleaned:
        return False

    # Strip currency symbols and signs
    for prefix in ("$", "€", "£", "¥", "₹", "+", "-"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()

    # Strip financial suffixes (case-insensitive)
    lower = cleaned.lower()
    for suffix in ("bps", "crore", "lakh", "bn", "mn", "cr", "%", "k", "m", "b", "x"):
        if lower.endswith(suffix):
            cleaned = cleaned[:-len(suffix)].strip()
            break

    # Remove separators and decimals
    cleaned = cleaned.replace(",", "").replace(".", "").replace("-", "")
    return cleaned.isdigit() and len(cleaned) > 0


def chunk_pages(content: DocumentContent, chunk_size: int = 3) -> List[dict]:
    """
    Group pages into overlapping chunks for LLM processing.
    Each chunk contains chunk_size consecutive pages with context.
    """
    chunks = []
    pages = content.pages
    step = max(1, chunk_size - 1)
    
    for i in range(0, len(pages), step):  # Overlap by 1 page
        chunk_pages = pages[i:i + chunk_size]
        if not chunk_pages:
            continue

        # Format the page number markers properly
        page_texts = []
        for p in chunk_pages:
            page_texts.append(f"--- Page {p.page_number} ---\n\n{p.text}")
        
        chunks.append({
            "text": "\n\n".join(page_texts),
            "page_numbers": [p.page_number for p in chunk_pages],
            "has_tables": any(p.has_tables for p in chunk_pages),
            "char_count": sum(p.char_count for p in chunk_pages),
            "word_count": sum(p.word_count for p in chunk_pages),
        })
    
    return chunks
