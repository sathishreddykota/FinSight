# backend/agent/judge.py

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from backend.agent.state import AgentState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=300
)

MAX_RETRIES = 2

JUDGE_PROMPT = """You are a financial research quality judge.

Given a question and retrieved context chunks, decide if the context
is sufficient to give a complete, accurate answer.

Return ONLY a JSON object like this:
{"sufficient": true, "reason": "Context covers all aspects of the question"}
or
{"sufficient": false, "reason": "Missing Microsoft revenue data for 2023"}"""


def judge_node(state: AgentState) -> AgentState:
    """
    Decides if retrieved chunks are sufficient to answer
    the original question. If not, triggers a retry.
    """
    question     = state["original_question"]
    final_chunks = state["final_chunks"]
    retry_count  = state.get("retry_count", 0)

    print(f"\n[JUDGE] Evaluating sufficiency (retry {retry_count})...")

    context_summary = ""
    for i, chunk in enumerate(final_chunks[:5]):
        context_summary += f"\nChunk {i+1} [{chunk.get('company')} {chunk.get('year')}]:\n"
        context_summary += chunk.get("text", "")[:300]
        context_summary += "\n"

    try:
        response = llm.invoke([
            SystemMessage(content=JUDGE_PROMPT),
            HumanMessage(content=f"""
Question: {question}

Retrieved context:
{context_summary}

Is this context sufficient to answer the question completely?
""")
        ])

        raw    = response.content.strip()
        raw    = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)

        is_sufficient = result.get("sufficient", False)
        reason        = result.get("reason", "")

        print(f"  Sufficient: {is_sufficient}")
        print(f"  Reason: {reason}")

        if retry_count >= MAX_RETRIES:
            print(f"  Max retries reached — proceeding anyway")
            is_sufficient = True

        return {
            **state,
            "is_sufficient": is_sufficient,
            "retry_count":   retry_count + 1
        }

    except Exception as e:
        print(f"  [JUDGE ERROR] {e}")
        return {
            **state,
            "is_sufficient": True,
            "retry_count":   retry_count + 1
        }