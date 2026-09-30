"""
LangGraph Cyclic State Machine for Autonomous Agentic Evaluation.
"""

import time
import os
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.guardrails import check_input_guardrail, evaluate_output_faithfulness
from memory.sqlite_store import SQLiteMemoryStore


def create_agent_graph(memory_store: SQLiteMemoryStore):
    workflow = StateGraph(AgentState)

    # Node 1: Deterministic Input Guardrail
    def input_guardrail_node(state: AgentState) -> dict:
        t0 = time.time()
        is_blocked, violation_code, reason = check_input_guardrail(state["query"])
        latency = int((time.time() - t0) * 1000)

        trace = list(state.get("execution_trace", []))
        trace.append({"node": "input_guardrail", "latency_ms": latency})

        if is_blocked:
            return {
                "guardrail_violation": violation_code,
                "final_output": reason,
                "execution_trace": trace,
            }
        return {"guardrail_violation": None, "execution_trace": trace}

    # Node 2: SQLite Factual Retrieval
    def retrieval_node(state: AgentState) -> dict:
        t0 = time.time()
        facts = memory_store.retrieve_grounding_facts(
            state["query"], pathname=state.get("pathname")
        )
        latency = int((time.time() - t0) * 1000)

        trace = list(state.get("execution_trace", []))
        trace.append({"node": "sqlite_retriever", "latency_ms": latency})

        return {"retrieved_facts": facts, "execution_trace": trace}

    # Node 3: Grounded Inference
    def inference_node(state: AgentState) -> dict:
        t0 = time.time()
        facts = state.get("retrieved_facts", [])
        facts_text = "\n".join([f"- {f['entity']}: {f['content']}" for f in facts])

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # Deterministic fallback when no API key is provided
            output = f"Grounded Context: {facts[0]['content'] if facts else 'No matching facts found.'}"
        else:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                prompt = f"""You are ARUN.AI, a high-density systems engineer. Answer in 2-3 sentences based strictly on these facts:
{facts_text}

User Question: {state['query']}"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                output = response.text.strip()
            except Exception as e:
                output = f"Execution grounded in memory: {facts[0]['content'] if facts else str(e)}"

        latency = int((time.time() - t0) * 1000)
        trace = list(state.get("execution_trace", []))
        trace.append({"node": "inference", "latency_ms": latency})

        return {"raw_response": output, "execution_trace": trace}

    # Node 4: Evaluation & Output Guardrail
    def eval_guardrail_node(state: AgentState) -> dict:
        t0 = time.time()
        raw = state.get("raw_response", "")
        facts = state.get("retrieved_facts", [])
        score, citations = evaluate_output_faithfulness(raw, facts)

        latency = int((time.time() - t0) * 1000)
        trace = list(state.get("execution_trace", []))
        trace.append({"node": "eval_guardrail", "latency_ms": latency})

        return {
            "eval_score": score,
            "citations": citations,
            "final_output": raw,
            "execution_trace": trace,
        }

    # Node 5: Session Persistence
    def persist_node(state: AgentState) -> dict:
        t0 = time.time()
        total_lat = sum(t["latency_ms"] for t in state.get("execution_trace", []))
        memory_store.persist_session_turn(
            session_id=state.get("session_id", "default"),
            query=state["query"],
            response=state.get("final_output", ""),
            eval_score=state.get("eval_score", 1.0),
            latency_ms=total_lat,
        )
        latency = int((time.time() - t0) * 1000)
        trace = list(state.get("execution_trace", []))
        trace.append({"node": "sqlite_persist", "latency_ms": latency})
        return {"execution_trace": trace}

    # Conditional Branch Router
    def route_after_input(state: AgentState) -> str:
        if state.get("guardrail_violation"):
            return "persist"
        return "retrieval"

    # Add Nodes
    workflow.add_node("input_guardrail", input_guardrail_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("inference", inference_node)
    workflow.add_node("eval_guardrail", eval_guardrail_node)
    workflow.add_node("persist", persist_node)

    # Set Entry Point & Edges
    workflow.set_entry_point("input_guardrail")
    workflow.add_conditional_edges("input_guardrail", route_after_input, {
        "persist": "persist",
        "retrieval": "retrieval",
    })
    workflow.add_edge("retrieval", "inference")
    workflow.add_edge("inference", "eval_guardrail")
    workflow.add_edge("eval_guardrail", "persist")
    workflow.add_edge("persist", END)

    return workflow.compile()
