"""
Embedded SQLite Factual Grounding & Session Memory Store.
"""

import sqlite3
import json
from typing import List, Dict, Any

DEFAULT_FACTS = [
    {
        "id": "fact-trading",
        "entity": "Algorithmic Trading Agent",
        "category": "project",
        "content": "Arun built the Algorithmic Trading Agent combining ARIMA and GARCH(1,1) volatility forecasting with FinBERT sentiment. Verified sub-32ms decision latency and automated stop-loss guardrails.",
        "target_route": "/systems/algorithmic-trading-agent",
        "claim_metric": "~5% MAPE on 30D Live Data, 31.8ms Latency",
    },
    {
        "id": "fact-rag",
        "entity": "Enterprise Document RAG",
        "category": "project",
        "content": "Arun engineered the Enterprise Document RAG System pairing BM25 keyword search with FAISS dense vector embeddings. Solved multi-process reader-writer lock contention on AWS EC2.",
        "target_route": "/systems/enterprise-rag-system",
        "claim_metric": "85% Research Time Reduction, Sub-1.2s P95 Latency",
    },
    {
        "id": "fact-finai",
        "entity": "AI Financial Analyst",
        "category": "project",
        "content": "Arun developed the AI Financial Analyst autonomously auditing SEC 10-K filings with Yahoo Finance market feeds, backed by strict mathematical balance sheet sanity checks.",
        "target_route": "/systems/ai-financial-analyst",
        "claim_metric": "100% SEC 10-K Data Integrity, Zero File Overwrite Race Conditions",
    },
    {
        "id": "fact-harness",
        "entity": "Autonomous Agentic Evaluation Harness",
        "category": "project",
        "content": "Self-hosted LangGraph cyclic evaluation harness with deterministic input guardrails, embedded SQLite memory, and real-time hallucination scoring running live on arunjyoticode.me.",
        "target_route": "/systems/agentic-audit-harness",
        "claim_metric": "100% Pass Injection Defense, 98.4% Grounding",
    },
]


class SQLiteMemoryStore:
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id TEXT PRIMARY KEY,
                    entity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    target_route TEXT NOT NULL,
                    claim_metric TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    eval_score REAL NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("SELECT COUNT(*) FROM knowledge_base")
            if cursor.fetchone()[0] == 0:
                for f in DEFAULT_FACTS:
                    cursor.execute("""
                        INSERT INTO knowledge_base (id, entity, category, content, target_route, claim_metric)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (f["id"], f["entity"], f["category"], f["content"], f["target_route"], f["claim_metric"]))
                conn.commit()

    def retrieve_grounding_facts(self, query: str, pathname: str = None) -> List[Dict[str, Any]]:
        words = [w.lower() for w in query.split() if len(w) > 3]
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, entity, category, content, target_route, claim_metric FROM knowledge_base")
            rows = cursor.fetchall()

        scored = []
        for r in rows:
            fact = {
                "id": r[0],
                "entity": r[1],
                "category": r[2],
                "content": r[3],
                "target_route": r[4],
                "claim_metric": r[5],
            }
            score = 0
            content_lower = fact["content"].lower()
            entity_lower = fact["entity"].lower()

            for w in words:
                if w in entity_lower:
                    score += 15
                elif w in content_lower:
                    score += 5

            if pathname and pathname in fact["target_route"]:
                score += 25

            if score > 0:
                scored.append((score, fact))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:3]]

    def persist_session_turn(self, session_id: str, query: str, response: str, eval_score: float, latency_ms: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_sessions (session_id, query, response, eval_score, latency_ms)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, query, response, eval_score, latency_ms))
            conn.commit()
