"""
Autonomous Agentic Evaluation & Guardrail Harness
State Schema definitions for LangGraph Cyclic Graph.
"""

from typing import TypedDict, List, Optional, Dict, Any


class Citation(TypedDict):
    id: str
    entity: str
    claim_metric: str
    target_route: str


class ExecutionTrace(TypedDict):
    node: str
    latency_ms: int


class AgentState(TypedDict):
    session_id: str
    query: str
    history: List[Dict[str, str]]
    pathname: Optional[str]
    retrieved_facts: List[Dict[str, Any]]
    raw_response: Optional[str]
    eval_score: Optional[float]
    guardrail_violation: Optional[str]
    citations: List[Citation]
    execution_trace: List[ExecutionTrace]
    final_output: Optional[str]
