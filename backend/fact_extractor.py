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


EXTRACTION_PROMPT = """You are an expert fact extraction system. Analyze the following text from the document "{doc_name}" and extract all meaningful factual claims.

For each fact, provide:
1. statement: A clear, standalone factual statement
2. value: The numerical value as a string (e.g. "7.5") or null if none
3. unit: The unit of measurement (%, USD Billion, etc.) or null
4. category: One of [GDP Growth, Inflation, Fiscal Policy, External Sector, Trade, Capital Flows, Monetary Policy, Employment, Financial Sector, Digital Payments, Sectoral Growth, Exchange Rate, Revenue, Profitability, Operations, Network Infrastructure, Workforce, Management, Corporate Information, Corporate History, Capital Markets, Market Position, Balance Sheet, General]
5. confidence: Your confidence score from 0.0 to 1.0
6. evidence_text: The exact quote from the text supporting this fact
7. page_numbers: Array of page numbers (e.g. [1] or [2, 3])
8. context: Object with time_period, scope, and methodology strings

Focus on numerical facts, key events, people, policies, and anything that could be compared across documents.

TEXT FROM PAGES {pages}:
---
{text}
---

Return ONLY a valid JSON array. No markdown, no code fences, no explanation."""


def _parse_json(text: str) -> list:
    """Robustly parse JSON, stripping markdown code fences if present."""
    text = text.strip()
    # Strip ```json ... ``` or ``` ... ```
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()
    # Find the JSON array boundaries
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end != -1 and end > start:
        text = text[start:end+1]
    return json.loads(text)


async def extract_facts_from_chunk(
    chunk: dict,
    doc_id: str,
    doc_name: str,
    api_key: Optional[str] = None
) -> List[Fact]:
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("WARNING: No GEMINI_API_KEY found!")
        return []

    chunk_text = chunk["text"].strip()
    if len(chunk_text) < 50:
        print(f"  Chunk too short ({len(chunk_text)} chars), skipping.")
        return []

    raw_text = ""
    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        prompt = EXTRACTION_PROMPT.format(
            doc_name=doc_name,
            pages=", ".join(str(p) for p in chunk["page_numbers"]),
            text=chunk_text[:10000]
        )

        response = await client.aio.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        raw_text = response.text
        print(f"  Gemini response: {len(raw_text)} chars")

        if not raw_text or len(raw_text) < 5:
            print(f"  WARNING: Empty response from Gemini")
            return []

        raw_facts = _parse_json(raw_text)
        print(f"  Parsed {len(raw_facts)} facts.")

        facts = []
        for raw in raw_facts:
            if not raw.get("statement"):
                continue
            ctx = raw.get("context") or {}
            if not isinstance(ctx, dict):
                ctx = {}
            facts.append(Fact(
                id=f"f-{uuid.uuid4().hex[:8]}",
                statement=raw["statement"],
                value=str(raw["value"]) if raw.get("value") is not None else None,
                unit=raw.get("unit") or "",
                category=raw.get("category") or "General",
                confidence=float(raw.get("confidence", 0.8)),
                source_doc_id=doc_id,
                source_doc_name=doc_name,
                page_numbers=raw.get("page_numbers") or chunk["page_numbers"],
                evidence_text=raw.get("evidence_text") or "",
                context=Context(
                    time_period=ctx.get("time_period", ""),
                    scope=ctx.get("scope", ""),
                    methodology=ctx.get("methodology", ""),
                )
            ))
        return facts

    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}. Raw: {repr(raw_text[:300])}")
        return []
    except Exception as e:
        print(f"  Fact extraction error ({type(e).__name__}): {e}")
        return []


async def extract_all_facts(
    chunks: List[dict],
    doc_id: str,
    doc_name: str,
    api_key: Optional[str] = None
) -> List[Fact]:
    import asyncio

    if not chunks:
        print("WARNING: No chunks provided!")
        return []

    print(f"Processing {len(chunks)} chunks for '{doc_name}'...")

    semaphore = asyncio.Semaphore(3)

    async def process(i, chunk):
        print(f"  Chunk {i+1}/{len(chunks)} pages={chunk['page_numbers']}...")
        async with semaphore:
            return await extract_facts_from_chunk(chunk, doc_id, doc_name, api_key)

    results = await asyncio.gather(*[process(i, c) for i, c in enumerate(chunks)], return_exceptions=True)

    all_facts = []
    for r in results:
        if isinstance(r, list):
            all_facts.extend(r)
        else:
            print(f"  Chunk raised: {type(r).__name__}: {r}")

    # Deduplicate
    seen, unique = set(), []
    for f in all_facts:
        key = f.statement.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(f)

    print(f"Total unique facts: {len(unique)}")
    return unique
