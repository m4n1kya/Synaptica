"""
Synaptica — Fact Extractor
LLM-powered fact extraction from PDF text chunks using Google Gemini.
"""
import json
import os
import uuid
from typing import List, Optional
from models import Fact, Context


# Extraction prompt template
EXTRACTION_PROMPT = """You are an expert fact extraction system. Analyze the following text from the document "{doc_name}" and extract all meaningful factual claims.

For each fact, provide:
1. statement: A clear, standalone factual statement
2. value: The numerical value (if any)
3. unit: The unit of measurement (%, USD Billion, ₹ Crore, etc.)
4. category: One of [GDP Growth, Inflation, Fiscal Policy, External Sector, Trade, Capital Flows, Monetary Policy, Employment, Financial Sector, Digital Payments, Sectoral Growth, Exchange Rate, Revenue, Profitability, Operations, Network Infrastructure, Workforce, Management, Corporate Information, Corporate History, Capital Markets, Market Position, Balance Sheet]
5. confidence: Your confidence in the extraction accuracy (0.0 to 1.0)
6. evidence_text: The exact quote from the source text that supports this fact
7. page_numbers: The page number(s) where this fact appears
8. context: An object with time_period, scope, and methodology

Focus on:
- Numerical facts (financial figures, percentages, counts, ratios)
- Semantic facts (key people, locations, policy positions, events)
- Facts that could be compared across documents

Return a JSON array of fact objects. If the text is too noisy or has no extractable facts, return an empty array.

TEXT FROM PAGES {pages}:
---
{text}
---

Return ONLY valid JSON, no markdown formatting."""


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
        return []  # No API key — demo mode uses pre-computed data

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = EXTRACTION_PROMPT.format(
            doc_name=doc_name,
            pages=", ".join(str(p) for p in chunk["page_numbers"]),
            text=chunk["text"][:12000]  # Limit text length for API
        )

        response = await model.generate_content_async(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.1,
            }
        )

        # Parse the JSON response
        raw_facts = json.loads(response.text)
        
        facts = []
        for raw in raw_facts:
            fact = Fact(
                id=f"f-{uuid.uuid4().hex[:8]}",
                statement=raw.get("statement", ""),
                value=str(raw.get("value", "")) if raw.get("value") is not None else None,
                unit=raw.get("unit", ""),
                category=raw.get("category", "General"),
                confidence=float(raw.get("confidence", 0.8)),
                source_doc_id=doc_id,
                source_doc_name=doc_name,
                page_numbers=raw.get("page_numbers", chunk["page_numbers"]),
                evidence_text=raw.get("evidence_text", ""),
                context=Context(
                    time_period=raw.get("context", {}).get("time_period", ""),
                    scope=raw.get("context", {}).get("scope", ""),
                    methodology=raw.get("context", {}).get("methodology", ""),
                )
            )
            facts.append(fact)
        
        return facts

    except Exception as e:
        print(f"Fact extraction error: {e}")
        return []


async def extract_all_facts(
    chunks: List[dict],
    doc_id: str,
    doc_name: str,
    api_key: Optional[str] = None
) -> List[Fact]:
    """Extract facts from all chunks of a document concurrently."""
    import asyncio
    
    # Limit concurrent API calls to avoid rate limiting (e.g. 5 concurrent)
    semaphore = asyncio.Semaphore(5)
    
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
        else:
            print(f"Error extracting chunk: {facts}")
    
    # Deduplicate by statement similarity (simple exact match)
    seen = set()
    unique_facts = []
    for fact in all_facts:
        key = fact.statement.lower().strip()
        if key not in seen:
            seen.add(key)
            unique_facts.append(fact)
    
    return unique_facts
