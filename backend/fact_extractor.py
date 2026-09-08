"""
Synaptica — Fact Extractor
LLM-powered fact extraction from PDF text chunks using Google Gemini.
"""
import json
import os
import re
import uuid
from typing import List, Optional
from models import Fact, Context


# Extraction prompt template
EXTRACTION_PROMPT = """You are an expert fact extraction system. Analyze the following text from the document "{doc_name}" and extract all meaningful factual claims.

For each fact, provide:
1. statement: A clear, standalone factual statement
2. value: The numerical value (if any, as a string like "7.5" or null)
3. unit: The unit of measurement (%, USD Billion, etc.) or null
4. category: One of [GDP Growth, Inflation, Fiscal Policy, External Sector, Trade, Capital Flows, Monetary Policy, Employment, Financial Sector, Digital Payments, Sectoral Growth, Exchange Rate, Revenue, Profitability, Operations, Network Infrastructure, Workforce, Management, Corporate Information, Corporate History, Capital Markets, Market Position, Balance Sheet, General]
5. confidence: Your confidence in the extraction accuracy (0.0 to 1.0)
6. evidence_text: The exact quote from the source text that supports this fact
7. page_numbers: Array of page numbers where this fact appears (e.g. [1] or [2, 3])
8. context: An object with time_period (string), scope (string), and methodology (string)

Focus on:
- Numerical facts (financial figures, percentages, counts, ratios)
- Semantic facts (key people, locations, policy positions, events)
- Facts that could be compared across documents

TEXT FROM PAGES {pages}:
---
{text}
---

Return ONLY a valid JSON array of fact objects. No markdown, no code blocks, no explanation."""


def _parse_gemini_json(text: str) -> list:
    """Robustly parse JSON from Gemini response, stripping markdown if needed."""
    text = text.strip()
    # Strip markdown code blocks if present
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    text = text.strip()
    # Find JSON array
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end != -1:
        text = text[start:end+1]
    return json.loads(text)


async def extract_facts_from_chunk(
    chunk: dict,
    doc_id: str,
    doc_name: str,
    api_key: Optional[str] = None
) -> List[Fact]:
    """
    Extract facts from a text chunk using Google Gemini.
    Falls back to empty list if no API key is available.
    """
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        print("WARNING: No GEMINI_API_KEY found in environment!")
        return []

    chunk_text = chunk["text"].strip()
    if len(chunk_text) < 50:
        print(f"  Chunk too short ({len(chunk_text)} chars), skipping.")
        return []

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = EXTRACTION_PROMPT.format(
            doc_name=doc_name,
            pages=", ".join(str(p) for p in chunk["page_numbers"]),
            text=chunk_text[:10000]  # Limit text length for API
        )

        print(f"  Calling Gemini for pages {chunk['page_numbers']}...")

        response = await model.generate_content_async(
            prompt,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 8192,
            }
        )

        raw_text = response.text
        print(f"  Gemini response length: {len(raw_text)} chars")
        if len(raw_text) < 10:
            print(f"  WARNING: Very short response: {repr(raw_text)}")
            return []

        raw_facts = _parse_gemini_json(raw_text)
        print(f"  Parsed {len(raw_facts)} facts from chunk.")

        facts = []
        for raw in raw_facts:
            if not raw.get("statement"):
                continue
            fact = Fact(
                id=f"f-{uuid.uuid4().hex[:8]}",
                statement=raw.get("statement", ""),
                value=str(raw["value"]) if raw.get("value") is not None else None,
                unit=raw.get("unit") or "",
                category=raw.get("category") or "General",
                confidence=float(raw.get("confidence", 0.8)),
                source_doc_id=doc_id,
                source_doc_name=doc_name,
                page_numbers=raw.get("page_numbers") or chunk["page_numbers"],
                evidence_text=raw.get("evidence_text") or "",
                context=Context(
                    time_period=raw.get("context", {}).get("time_period", "") if isinstance(raw.get("context"), dict) else "",
                    scope=raw.get("context", {}).get("scope", "") if isinstance(raw.get("context"), dict) else "",
                    methodology=raw.get("context", {}).get("methodology", "") if isinstance(raw.get("context"), dict) else "",
                )
            )
            facts.append(fact)

        return facts

    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}. Raw response: {repr(raw_text[:500])}")
        return []
    except Exception as e:
        print(f"  Fact extraction error (type={type(e).__name__}): {e}")
        return []


async def extract_all_facts(
    chunks: List[dict],
    doc_id: str,
    doc_name: str,
    api_key: Optional[str] = None
) -> List[Fact]:
    """Extract facts from all chunks of a document concurrently."""
    import asyncio

    if not chunks:
        print("WARNING: No chunks to process!")
        return []

    print(f"Processing {len(chunks)} chunk(s) for doc '{doc_name}'...")

    # Limit concurrent API calls to avoid rate limiting
    semaphore = asyncio.Semaphore(3)

    async def process_chunk_with_semaphore(i: int, chunk: dict):
        print(f"  Extracting chunk {i+1}/{len(chunks)} (pages {chunk['page_numbers']})...")
        async with semaphore:
            return await extract_facts_from_chunk(chunk, doc_id, doc_name, api_key)

    tasks = [process_chunk_with_semaphore(i, chunk) for i, chunk in enumerate(chunks)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_facts = []
    for facts in results:
        if isinstance(facts, list):
            all_facts.extend(facts)
        elif isinstance(facts, Exception):
            print(f"  Chunk task raised exception: {type(facts).__name__}: {facts}")

    # Deduplicate by statement similarity (simple exact match)
    seen = set()
    unique_facts = []
    for fact in all_facts:
        key = fact.statement.lower().strip()
        if key not in seen:
            seen.add(key)
            unique_facts.append(fact)

    print(f"Total unique facts extracted: {len(unique_facts)}")
    return unique_facts
