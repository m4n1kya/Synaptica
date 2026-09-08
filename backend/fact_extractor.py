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


EXTRACTION_PROMPT = """You are a data extraction assistant. Extract factual information from the following document text.

For each fact found, output a JSON object with these fields:
- statement: the factual claim as a clear sentence
- value: numeric value as string, or null
- unit: unit of measurement, or null
- category: one of [Revenue, Profitability, Operations, Workforce, Management, Corporate Information, Corporate History, Capital Markets, Market Position, Balance Sheet, GDP Growth, Inflation, Fiscal Policy, External Sector, Trade, Employment, Financial Sector, Network Infrastructure, General]
- confidence: number from 0.0 to 1.0
- evidence_text: exact quote from the text
- page_numbers: array of integers
- context: object with time_period, scope, methodology (all strings)

Document: {doc_name}
Pages: {pages}

Text:
{text}

Output ONLY a JSON array of fact objects. If no facts exist, output [].
Do not include any explanation or markdown."""


def _parse_json(text: str) -> list:
    """Robustly parse JSON, stripping markdown code fences if present."""
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end != -1 and end > start:
        text = text[start:end+1]
    return json.loads(text)


def _safe_response_text(response) -> Optional[str]:
    """Safely extract text from a Gemini response, handling blocked/empty responses."""
    try:
        # Check if candidates exist and have content
        if not response.candidates:
            print("  WARNING: No candidates in response (blocked or empty)")
            return None
        
        candidate = response.candidates[0]
        
        # Check finish reason
        finish_reason = str(candidate.finish_reason) if hasattr(candidate, 'finish_reason') else "UNKNOWN"
        if "SAFETY" in finish_reason or "BLOCK" in finish_reason:
            print(f"  WARNING: Response blocked by safety filter: {finish_reason}")
            return None
        
        # Try to get text
        if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
            return "".join(p.text for p in candidate.content.parts if hasattr(p, 'text'))
        
        # Fallback: try response.text directly
        return response.text
        
    except Exception as e:
        print(f"  WARNING: Could not extract response text: {e}")
        return None


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
    
    # Retry up to 3 times with exponential backoff for 503/429
    import asyncio
    for attempt in range(3):
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            prompt = EXTRACTION_PROMPT.format(
                doc_name=doc_name,
                pages=", ".join(str(p) for p in chunk["page_numbers"]),
                text=chunk_text[:10000]
            )

            response = await client.aio.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=8192,
                    safety_settings=[
                        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                    ],
                )
            )

            raw_text = _safe_response_text(response)
            if not raw_text:
                return []

            print(f"  Gemini response: {len(raw_text)} chars")
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
            err_str = str(e)
            if ("503" in err_str or "UNAVAILABLE" in err_str or
                "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or
                "quota" in err_str.lower()):
                wait = (2 ** attempt) * 10  # 10s, 20s, 40s
                print(f"  Rate limit/overload (attempt {attempt+1}/3), retrying in {wait}s...")
                await asyncio.sleep(wait)
                continue
            print(f"  Fact extraction error ({type(e).__name__}): {e}")
            return []
    
    print(f"  All 3 attempts failed for chunk pages={chunk['page_numbers']}")
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

    all_facts = []
    # Process SEQUENTIALLY to avoid rate limits on free tier
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}/{len(chunks)} pages={chunk['page_numbers']}...")
        facts = await extract_facts_from_chunk(chunk, doc_id, doc_name, api_key)
        all_facts.extend(facts)
        # Small delay between chunks to avoid rate limiting
        if i < len(chunks) - 1:
            await asyncio.sleep(1)

    # Deduplicate
    seen, unique = set(), []
    for f in all_facts:
        key = f.statement.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(f)

    print(f"Total unique facts: {len(unique)}")
    return unique

