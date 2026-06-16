# backend/agent/synthesizer.py

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from backend.agent.state import AgentState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=2000
)

SYNTHESIZER_PROMPT = """You are FinSight, an expert financial research assistant.

You answer complex questions about Big Tech companies using ONLY the provided
context from official SEC 10-K filings and earnings reports.

Rules:
- Base your answer strictly on the provided context
- Always cite which company and year each fact comes from
- Use specific numbers and figures when available
- Structure your answer clearly with sections if needed
- If context is insufficient for any part, say so explicitly
- Never make up financial figures

Format your answer as:
## Answer
[Your detailed answer here]

## Key Facts
- [Fact 1 with source]
- [Fact 2 with source]

## Sources Used
- [Company, Year, Document type]"""


def build_context(final_chunks: list[dict]) -> str:
    context = ""
    for i, chunk in enumerate(final_chunks):
        context += f"\n---\n"
        context += f"Source {i+1}: {chunk.get('company')} | {chunk.get('year')} | {chunk.get('doc_type', '10-K')}\n"
        context += f"{chunk.get('text', '')}\n"
    return context


def extract_sources(final_chunks: list[dict]) -> list[dict]:
    seen    = set()
    sources = []
    for chunk in final_chunks:
        key = f"{chunk.get('company')}_{chunk.get('year')}"
        if key not in seen:
            seen.add(key)
            sources.append({
                "company":  chunk.get("company"),
                "ticker":   chunk.get("ticker"),
                "year":     chunk.get("year"),
                "doc_type": chunk.get("doc_type", "10-K")
            })
    return sources


def synthesizer_node(state: AgentState) -> AgentState:
    question     = state["original_question"]
    final_chunks = state["final_chunks"]

    print(f"\n[SYNTHESIZER] Generating answer...")
    print(f"  Using {len(final_chunks)} chunks")

    context = build_context(final_chunks)
    sources = extract_sources(final_chunks)

    try:
        response = llm.invoke([
            SystemMessage(content=SYNTHESIZER_PROMPT),
            HumanMessage(content=f"""
Question: {question}

Context from SEC filings:
{context}

Please provide a comprehensive, well-cited answer.
""")
        ])

        answer = response.content.strip()
        print(f"  ✅ Answer generated ({len(answer)} chars)")

        return {
            **state,
            "final_answer": answer,
            "sources":      sources
        }

    except Exception as e:
        print(f"  [SYNTHESIZER ERROR] {e}")
        return {
            **state,
            "final_answer": f"Error generating answer: {e}",
            "sources":      sources
        }