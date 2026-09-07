"""
Synaptica — PDF Processor
Extracts text content from PDF files with page-level metadata using PyMuPDF.
"""
import os
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class PageContent:
    """Extracted content from a single PDF page."""
    page_number: int
    text: str
    char_count: int = 0
    has_tables: bool = False
    has_images: bool = False


@dataclass
class DocumentContent:
    """Complete extracted content from a PDF document."""
    filename: str
    total_pages: int
    pages: List[PageContent] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


def extract_pdf_text(filepath: str) -> Optional[DocumentContent]:
    """
    Extract text from a PDF file using pypdf.
    Returns structured content with per-page text and metadata.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        print("WARNING: pypdf not installed. Install with: pip install pypdf")
        return None

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None

    try:
        reader = PdfReader(filepath)
        meta = reader.metadata or {}
        
        content = DocumentContent(
            filename=os.path.basename(filepath),
            total_pages=len(reader.pages),
            metadata={
                "title": meta.get("/Title", ""),
                "author": meta.get("/Author", ""),
                "subject": meta.get("/Subject", ""),
                "creator": meta.get("/Creator", ""),
            }
        )

        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            
            # Detect if page has tables (heuristic: multiple tab/aligned columns)
            has_tables = text.count("\t") > 5 or _detect_table_pattern(text)
            
            # Detect if page has images (pypdf has page.images)
            has_images = len(page.images) > 0 if hasattr(page, 'images') else False

            content.pages.append(PageContent(
                page_number=i + 1,  # 1-indexed
                text=text.strip(),
                char_count=len(text),
                has_tables=has_tables,
                has_images=has_images
            ))

        return content

    except Exception as e:
        print(f"Error processing PDF {filepath}: {e}")
        return None


def _detect_table_pattern(text: str) -> bool:
    """Heuristic to detect table-like patterns in extracted text."""
    lines = text.split("\n")
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
    """Check if a token looks like a number (including formatted ones)."""
    cleaned = token.replace(",", "").replace(".", "").replace("-", "").replace("%", "").replace("₹", "")
    return cleaned.isdigit() and len(cleaned) > 0


def chunk_pages(content: DocumentContent, chunk_size: int = 3) -> List[dict]:
    """
    Group pages into overlapping chunks for LLM processing.
    Each chunk contains chunk_size consecutive pages with context.
    """
    chunks = []
    pages = content.pages
    
    for i in range(0, len(pages), chunk_size - 1):  # Overlap by 1 page
        chunk_pages = pages[i:i + chunk_size]
        if not chunk_pages:
            continue
        
        combined_text = "\n\n--- Page {} ---\n\n".join(
            [p.text for p in chunk_pages]
        )
        # Format the page number markers properly
        page_texts = []
        for p in chunk_pages:
            page_texts.append(f"--- Page {p.page_number} ---\n\n{p.text}")
        
        chunks.append({
            "text": "\n\n".join(page_texts),
            "page_numbers": [p.page_number for p in chunk_pages],
            "has_tables": any(p.has_tables for p in chunk_pages),
            "char_count": sum(p.char_count for p in chunk_pages),
        })
    
    return chunks
