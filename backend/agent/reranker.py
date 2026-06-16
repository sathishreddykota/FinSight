# backend/agent/reranker.py

from flashrank import Ranker, RerankRequest
from backend.agent.state import AgentState

# Load reranker model once
ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2")

MAX_FINAL_CHUNKS = 8  # max chunks to send to LLM


def reranker_node(state: AgentState) -> AgentState:
    """
    Takes all retrieved chunks, reranks them against the
    original question, deduplicates, and returns the best ones.
    """
    question       = state["original_question"]
    retrieved      = state["retrieved_chunks"]

    print(f"\n[RERANKER] Reranking chunks...")

    # Flatten all chunks from all sub-questions
    all_chunks = []
    for item in retrieved:
        for chunk in item["chunks"]:
            all_chunks.append(chunk)

    print(f"  Total chunks before reranking: {len(all_chunks)}")

    # Deduplicate by text content
    seen_texts = set()
    unique_chunks = []
    for chunk in all_chunks:
        text_key = chunk["text"][:100]  # first 100 chars as key
        if text_key not in seen_texts:
            seen_texts.add(text_key)
            unique_chunks.append(chunk)

    print(f"  After deduplication: {len(unique_chunks)} chunks")

    # Rerank using FlashRank
    passages = [{"text": c["text"], "meta": c} for c in unique_chunks]

    rerank_request = RerankRequest(
        query=question,
        passages=passages
    )

    reranked = ranker.rerank(rerank_request)

    # Take top MAX_FINAL_CHUNKS
    final_chunks = []
    for r in reranked[:MAX_FINAL_CHUNKS]:
        chunk_data = r.get("meta", {})
        chunk_data["rerank_score"] = r.get("score", 0)
        final_chunks.append(chunk_data)

    print(f"  Final chunks after reranking: {len(final_chunks)}")
    for i, c in enumerate(final_chunks):
        print(f"    {i+1}. {c.get('company')} {c.get('year')} — score: {c.get('rerank_score', 0):.4f}")

    return {
        **state,
        "final_chunks": final_chunks
    }