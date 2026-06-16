# backend/agent/retriever.py

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from fastembed import TextEmbedding
from backend.agent.state import AgentState

load_dotenv()

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "finsight")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
TOP_K           = 5  # retrieve top 5 chunks per sub-question

# Initialize once at module level (avoid reloading model every call)
client   = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
embedder = TextEmbedding(EMBEDDING_MODEL)


def retrieve_for_query(query: str) -> list[dict]:
    """Retrieve top-k chunks for a single query."""
    query_vec = list(embedder.embed([query]))[0].tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vec,
        limit=TOP_K
    ).points

    chunks = []
    for r in results:
        chunks.append({
            "text":    r.payload.get("text", ""),
            "score":   r.score,
            "company": r.payload.get("company", ""),
            "ticker":  r.payload.get("ticker", ""),
            "year":    r.payload.get("year", ""),
            "doc_type": r.payload.get("doc_type", "10-K"),
            "source":  r.payload.get("source", "")
        })

    return chunks


def retriever_node(state: AgentState) -> AgentState:
    """
    Runs retrieval for each sub-question and collects all chunks.
    """
    sub_questions = state["sub_questions"]
    print(f"\n[RETRIEVER] Retrieving for {len(sub_questions)} sub-questions...")

    all_retrieved = []

    for i, sub_q in enumerate(sub_questions):
        print(f"  Sub-question {i+1}: {sub_q[:80]}...")
        chunks = retrieve_for_query(sub_q)
        print(f"    → {len(chunks)} chunks retrieved")

        all_retrieved.append({
            "sub_question": sub_q,
            "chunks":       chunks
        })

    return {
        **state,
        "retrieved_chunks": all_retrieved
    }