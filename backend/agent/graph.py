# backend/agent/graph.py

from langgraph.graph import StateGraph, END
from backend.agent.state import AgentState
from backend.agent.planner import planner_node
from backend.agent.retriever import retriever_node
from backend.agent.reranker import reranker_node
from backend.agent.judge import judge_node
from backend.agent.synthesizer import synthesizer_node


def should_retry(state: AgentState) -> str:
    """
    Router function — decides whether to retry retrieval
    or proceed to synthesis based on judge's decision.
    """
    if state.get("is_sufficient", False):
        return "synthesize"
    else:
        return "retry"


def build_graph() -> StateGraph:
    """Build and compile the agentic RAG graph."""

    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("planner",     planner_node)
    graph.add_node("retriever",   retriever_node)
    graph.add_node("reranker",    reranker_node)
    graph.add_node("judge",       judge_node)
    graph.add_node("synthesizer", synthesizer_node)

    # Define the flow
    graph.set_entry_point("planner")

    graph.add_edge("planner",   "retriever")
    graph.add_edge("retriever", "reranker")
    graph.add_edge("reranker",  "judge")

    # Conditional edge — retry or synthesize
    graph.add_conditional_edges(
        "judge",
        should_retry,
        {
            "synthesize": "synthesizer",
            "retry":      "planner"      # loop back to planner
        }
    )

    graph.add_edge("synthesizer", END)

    return graph.compile()


# Compile once at module level
agent = build_graph()


def run_agent(question: str) -> dict:
    """
    Main entry point — run the full agentic RAG pipeline.
    """
    print(f"\n{'='*60}")
    print(f"FINSIGHT AGENT")
    print(f"{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}")

    initial_state: AgentState = {
        "original_question": question,
        "sub_questions":     [],
        "retrieved_chunks":  [],
        "final_chunks":      [],
        "is_sufficient":     False,
        "retry_count":       0,
        "final_answer":      "",
        "sources":           [],
        "error":             ""
    }

    result = agent.invoke(initial_state)

    return {
        "question":     result["original_question"],
        "answer":       result["final_answer"],
        "sources":      result["sources"],
        "sub_questions": result["sub_questions"],
        "retry_count":  result["retry_count"]
    }