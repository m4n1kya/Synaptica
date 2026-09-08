"""
Synaptica — Fact Linker
Cross-document fact comparison and relationship classification using LLM.
"""
import json
import os
import re
import uuid
from typing import List, Optional, Tuple
from models import Fact, Relationship



LINKING_PROMPT = """You are an expert at comparing facts across documents. Given two facts from different sources, determine their relationship.

FACT A (from {doc_a}):
- Statement: {statement_a}
- Value: {value_a} {unit_a}
- Category: {category_a}
- Time Period: {period_a}
- Scope: {scope_a}
- Evidence: "{evidence_a}"

FACT B (from {doc_b}):
- Statement: {statement_b}
- Value: {value_b} {unit_b}
- Category: {category_b}
- Time Period: {period_b}
- Scope: {scope_b}
- Evidence: "{evidence_b}"

Classify the relationship as one of:
1. "corroborates" — Same fact confirmed by independent source (may use different wording)
2. "contradicts" — Conflicting values/claims about the same subject, period, and scope
3. "contextual_difference" — Apparent contradiction explained by different time periods, scope, methodology, or units
4. "unrelated" — Facts are about different topics and have no meaningful relationship

Return a JSON object with:
- relationship_type: one of the above
- explanation: detailed explanation of why this classification was chosen
- confidence: 0.0 to 1.0
- reconciliation: if contextual_difference, explain how to reconcile the facts (null otherwise)
- reasoning_trace: step-by-step reasoning

Return ONLY valid JSON."""


def find_candidate_pairs(facts: List[Fact]) -> List[Tuple[Fact, Fact]]:
    """Find fact pairs that are likely related based on category and value matching."""
    pairs = []
    for i, fact_a in enumerate(facts):
        for j, fact_b in enumerate(facts):
            if j <= i:
                continue
            # Only compare facts from different documents
            if fact_a.source_doc_id == fact_b.source_doc_id:
                continue
            # Check if categories match or overlap
            if fact_a.category == fact_b.category:
                pairs.append((fact_a, fact_b))
            # Check for value overlap (same numeric value)
            elif (fact_a.value and fact_b.value and 
                  fact_a.value == fact_b.value and 
                  fact_a.unit == fact_b.unit):
                pairs.append((fact_a, fact_b))
    return pairs


async def classify_relationship(
    fact_a: Fact, 
    fact_b: Fact,
    api_key: Optional[str] = None
) -> Optional[Relationship]:
    """Use LLM to classify the relationship between two facts."""
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    
    if not api_key:
        return None

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        prompt = LINKING_PROMPT.format(
            doc_a=fact_a.source_doc_name,
            statement_a=fact_a.statement,
            value_a=fact_a.value or "N/A",
            unit_a=fact_a.unit or "",
            category_a=fact_a.category,
            period_a=fact_a.context.time_period,
            scope_a=fact_a.context.scope,
            evidence_a=fact_a.evidence_text[:500],
            doc_b=fact_b.source_doc_name,
            statement_b=fact_b.statement,
            value_b=fact_b.value or "N/A",
            unit_b=fact_b.unit or "",
            category_b=fact_b.category,
            period_b=fact_b.context.time_period,
            scope_b=fact_b.context.scope,
            evidence_b=fact_b.evidence_text[:500],
        )

        response = await client.aio.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        raw = response.text.strip()
        raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
        raw = re.sub(r'\s*```\s*$', '', raw, flags=re.MULTILINE)
        result = json.loads(raw)
        
        if result.get("relationship_type") == "unrelated":
            return None

        return Relationship(
            id=f"rel-{uuid.uuid4().hex[:8]}",
            fact_a_id=fact_a.id,
            fact_b_id=fact_b.id,
            relationship_type=result["relationship_type"],
            explanation=result.get("explanation", ""),
            confidence=float(result.get("confidence", 0.8)),
            reconciliation=result.get("reconciliation"),
            reasoning_trace=result.get("reasoning_trace"),
        )

    except Exception as e:
        print(f"Linking error: {e}")
        return None


async def link_all_facts(
    facts: List[Fact],
    api_key: Optional[str] = None
) -> List[Relationship]:
    """Find and classify all cross-document fact relationships concurrently."""
    import asyncio
    pairs = find_candidate_pairs(facts)
    print(f"  Found {len(pairs)} candidate pairs for comparison...")
    
    semaphore = asyncio.Semaphore(10)
    
    async def process_pair_with_semaphore(i: int, fact_a: Fact, fact_b: Fact):
        print(f"  Analyzing pair {i+1}/{len(pairs)}...")
        async with semaphore:
            return await classify_relationship(fact_a, fact_b, api_key)
            
    tasks = [process_pair_with_semaphore(i, fact_a, fact_b) for i, (fact_a, fact_b) in enumerate(pairs)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    relationships = []
    for rel in results:
        if isinstance(rel, Relationship):
            relationships.append(rel)
        elif isinstance(rel, Exception):
            print(f"Error linking pair: {rel}")
            
    return relationships


def find_candidate_pairs_incremental(new_facts: List[Fact], existing_facts: List[Fact]) -> List[Tuple[Fact, Fact]]:
    """Find fact pairs between new facts and existing facts."""
    pairs = []
    for fact_a in new_facts:
        for fact_b in existing_facts:
            # Only compare facts from different documents
            if fact_a.source_doc_id == fact_b.source_doc_id:
                continue
            # Check if categories match or overlap
            if fact_a.category == fact_b.category:
                pairs.append((fact_a, fact_b))
            # Check for value overlap (same numeric value)
            elif (fact_a.value and fact_b.value and 
                  fact_a.value == fact_b.value and 
                  fact_a.unit == fact_b.unit):
                pairs.append((fact_a, fact_b))
    return pairs


async def link_incremental(
    new_facts: List[Fact],
    existing_facts: List[Fact],
    api_key: Optional[str] = None
) -> List[Relationship]:
    """Find and classify relationships only for newly added facts concurrently."""
    import asyncio
    pairs = find_candidate_pairs_incremental(new_facts, existing_facts)
    print(f"  Found {len(pairs)} candidate pairs for incremental linking...")
    
    semaphore = asyncio.Semaphore(10)
    
    async def process_pair_with_semaphore(i: int, fact_a: Fact, fact_b: Fact):
        print(f"  Analyzing incremental pair {i+1}/{len(pairs)}...")
        async with semaphore:
            return await classify_relationship(fact_a, fact_b, api_key)
            
    tasks = [process_pair_with_semaphore(i, fact_a, fact_b) for i, (fact_a, fact_b) in enumerate(pairs)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    relationships = []
    for rel in results:
        if isinstance(rel, Relationship):
            relationships.append(rel)
        elif isinstance(rel, Exception):
            print(f"Error linking pair: {rel}")
            
    return relationships
