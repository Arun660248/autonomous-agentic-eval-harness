"""
CLI Entrypoint for Autonomous Agentic Evaluation & Guardrail Harness.
"""

import sys
import uuid

# Ensure utf-8 output handling across Windows, Linux, and macOS
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from memory.sqlite_store import SQLiteMemoryStore
from agent.graph import create_agent_graph


def main():
    print("=" * 60)
    print("  AUTONOMOUS AGENTIC EVALUATION & GUARDRAIL HARNESS")
    print("  Live Production Demo: https://www.arunjyoticode.me")
    print("=" * 60)

    store = SQLiteMemoryStore()
    app = create_agent_graph(store)
    session_id = f"cli-{uuid.uuid4().hex[:8]}"

    print("\nSystem online. Enter a query or try an adversarial prompt attack.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            query = input("user@harness> ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                break

            initial_state = {
                "session_id": session_id,
                "query": query,
                "history": [],
                "pathname": "/",
                "retrieved_facts": [],
                "raw_response": None,
                "eval_score": None,
                "guardrail_violation": None,
                "citations": [],
                "execution_trace": [],
                "final_output": None,
            }

            result = app.invoke(initial_state)

            if result.get("guardrail_violation"):
                print(f"\n[GUARDRAIL INTERCEPTED]: {result['guardrail_violation']}")
                print(f"Details: {result['final_output']}\n")
            else:
                print(f"\n[AGENT]: {result.get('final_output')}")
                if result.get("citations"):
                    print(f"Citations: {[c['entity'] for c in result['citations']]}")
                print(f"Factual Consistency Score: {result.get('eval_score', 1.0) * 100:.1f}%\n")

            traces = " -> ".join([f"{t['node']} ({t['latency_ms']}ms)" for t in result.get("execution_trace", [])])
            print(f"Execution Trace: {traces}\n")

        except (KeyboardInterrupt, EOFError):
            break

    print("\nHarness shutdown cleanly.")


if __name__ == "__main__":
    main()
