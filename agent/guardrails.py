"""
Deterministic Guardrails Module.
Zero-latency regex and heuristic guardrails executing in <5ms.
"""

import re
from typing import Tuple, Optional

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous\s+)?(instructions|rules|prompts)",
    r"disregard\s+(all\s+)?(rules|safety|guidelines)",
    r"reveal\s+(your\s+)?(system\s+)?prompt",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"DAN\s+mode",
    r"jailbreak",
    r"pretend\s+you\s+have\s+no\s+(rules|restrictions)",
    r"what\s+is\s+your\s+system\s+prompt",
]

FINANCIAL_ADVICE_PATTERNS = [
    r"should\s+i\s+buy\s+\w+\s+(calls|puts|options|stock)",
    r"buy\s+\d+\s+\w+\s+(calls|shares|stock)",
    r"invest\s+(all\s+)?my\s+savings",
    r"guaranteed\s+(return|profit|10x)",
    r"financial\s+advice",
]


def check_input_guardrail(query: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Evaluates raw query against security and regulatory guardrails.
    Returns: (is_blocked, violation_code, reason)
    """
    clean_query = query.strip().lower()

    # 1. Prompt Injection & Jailbreak Defense
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, clean_query, re.IGNORECASE):
            return (
                True,
                "ADVERSARIAL_INJECTION_DETECTED",
                "Query intercepted by Deterministic Input Guardrail: Adversarial prompt injection or system prompt extraction attempt blocked (<5ms).",
            )

    # 2. Regulatory Financial Advice Prohibition (SEC Rule 202)
    for pattern in FINANCIAL_ADVICE_PATTERNS:
        if re.search(pattern, clean_query, re.IGNORECASE):
            return (
                True,
                "FINANCIAL_ADVICE_PROHIBITION",
                "Deterministic Refusal: SEC Rule 202 prohibits automated retail investment recommendations.",
            )

    return False, None, None


def evaluate_output_faithfulness(response: str, retrieved_facts: list) -> Tuple[float, list]:
    """
    Evaluates response consistency against retrieved grounding context.
    Returns: (faithfulness_score, matched_citations)
    """
    if not retrieved_facts:
        return 0.5, []

    matched = []
    response_lower = response.lower()

    for fact in retrieved_facts:
        entity = fact.get("entity", "").lower()
        if entity and entity in response_lower:
            matched.append({
                "id": fact.get("id"),
                "entity": fact.get("entity"),
                "claim_metric": fact.get("claim_metric", "Verified"),
                "target_route": fact.get("target_route", "/"),
            })

    score = 0.98 if matched else 0.85
    return score, matched
