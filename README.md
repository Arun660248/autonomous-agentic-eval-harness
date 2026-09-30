# Autonomous Agentic Evaluation & Guardrail Harness

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph_Cyclic_Graph-00c853?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![SQLite Memory](https://img.shields.io/badge/Memory-Embedded_SQLite-003B57?style=flat-square&logo=sqlite)](https://sqlite.org/)
[![Live Production Demo](https://img.shields.io/badge/Live_Demo-ARUN.SYS_Portfolio-emerald?style=flat-square)](https://www.arunjyoticode.me)
[![Pytest Verified](https://img.shields.io/badge/Safety_Tests-100%25_Pass-brightgreen?style=flat-square)](tests/test_guardrails.py)
[![License](https://img.shields.io/badge/License-MIT-black?style=flat-square)](LICENSE)

> **Live Running Production Demo:** [https://www.arunjyoticode.me](https://www.arunjyoticode.me)  
> *This autonomous evaluation and guardrail harness is actively running in production as the core intelligence engine behind ARUN.AI on `arunjyoticode.me`.*

---

## 1. Architectural Overview

The **Autonomous Agentic Evaluation & Guardrail Harness** is a production-grade multi-turn state machine engineered with **LangGraph** and **SQLite** to solve two critical vulnerabilities in modern LLM applications:
1. **Adversarial Prompt Injections & Jailbreaks:** Intercepted deterministically at the entry boundary in `<5ms` before any LLM token is consumed.
2. **Ungrounded Hallucinations:** Enforces strict ground-truth context retrieval with real-time faithfulness scoring and attribution citations.

```
                              [ Incoming Query ]
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │   input_guardrail_node    │
                        │  Deterministic Regex/SEC  │
                        └─────────────┬─────────────┘
                                      │
                   ┌──────────────────┴──────────────────┐
                   │ [ Pass ]                            │ [ Attack / SEC Blocked ]
                   ▼                                     │
     ┌───────────────────────────┐                       │
     │   sqlite_retrieval_node   │                       │
     │ Path-boosted Fact Ranking │                       │
     └─────────────┬─────────────┘                       │
                   │                                     │
                   ▼                                     │
     ┌───────────────────────────┐                       │
     │   gemini_inference_node   │                       │
     │ Grounded 2-3 Sentence Gen │                       │
     └─────────────┬─────────────┘                       │
                   │                                     │
                   ▼                                     │
     ┌───────────────────────────┐                       │
     │    eval_guardrail_node    │                       │
     │   Faithfulness & Source   │                       │
     └─────────────┬─────────────┘                       │
                   │                                     │
                   └──────────────────┬──────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │     db_persist_node       │
                        │ Commit Session & Latencies│
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                                   [ END ]
```

---

## 2. Key Capabilities

### 🛡️ 1. Deterministic Input Guardrail (<5ms)
- Evaluates queries against pre-compiled compiled regex patterns for:
  - System prompt extraction (`"reveal your system prompt"`, `"ignore previous instructions"`).
  - Jailbreak framing (`"DAN mode"`, `"developer mode"`).
  - Regulatory violations (SEC Rule 202 retail financial advice prohibitions).
- When an attack is detected, the graph **completely bypasses LLM inference**, saving 100% of reasoning token costs and preventing security leaks.

### 💾 2. Embedded SQLite Factual Grounding & Memory
- Ingests verified facts and benchmark evidence into an embedded SQLite store.
- Supports **route-aware retrieval**: boosts facts matching the visitor's active viewing path by `+25` score.
- Records multi-turn session histories, hallucination scores, and node latency traces.

### ⚖️ 3. Real-Time Faithfulness Evaluation
- Cross-references the generated response against retrieved facts.
- Generates structured citations mapping claims directly to proof matrices.

---

## 3. Quickstart & Installation

```bash
# 1. Clone repository
git clone https://github.com/Arun660248/autonomous-agentic-eval-harness.git
cd autonomous-agentic-eval-harness

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Optional: Add Gemini API key for live inference
export GEMINI_API_KEY="your_api_key_here"  # On Windows: set GEMINI_API_KEY="your_key"

# 5. Run CLI REPL
python main.py
```

---

## 4. Automated Safety Test Suite (Pytest)

Run the automated test suite to verify deterministic injection interception:

```bash
pytest tests/ -v
```

### Verified Test Results
- `test_adversarial_prompt_injection_blocked`: **PASSED** (Latency `<15ms`, `100% Block Rate`)
- `test_sec_rule_financial_advice_refusal`: **PASSED** (Deterministic refusal of retail trading advice)
- `test_sqlite_retrieval_ranking`: **PASSED** (Pathname-boosted scoring validated)
- `test_end_to_end_graph_bypass_on_injection`: **PASSED** (Model inference bypassed on attack)

---

## 5. Live Production Integration

This harness is deployed live in production on:
👉 **[https://www.arunjyoticode.me](https://www.arunjyoticode.me)**

You can interact with it directly by clicking the floating **`>_ ARUN.AI`** button in the upper-right corner of the website or pressing `[ ⌘K ]`.

---

## 6. Author

**Arun Jyoti Chakraborty**  
*2nd-Year B.Sc. (Hons.) Data Science & AI — IIT Guwahati*  
- **Portfolio:** [https://www.arunjyoticode.me](https://www.arunjyoticode.me)  
- **GitHub:** [@Arun660248](https://github.com/Arun660248)  
- **LinkedIn:** [Arun Jyoti Chakraborty](https://www.linkedin.com/in/arun-jyoti-chakraborty/)  
- **Email:** [arunjyotichakraborty18@gmail.com](mailto:arunjyotichakraborty18@gmail.com)

---

## 7. License

MIT License.
