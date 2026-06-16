# backend/agent/planner.py

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
    max_tokens=1000
)

PLANNER_SYSTEM_PROMPT = """You are a financial research query planner.

Your job is to decompose a complex financial question into 2-4 specific sub-questions
that can each be answered by retrieving from SEC 10-K filings.

Rules:
- Each sub-question must be self-contained and specific
- Focus on facts that would appear in annual reports
- Include company names and years when relevant
- Return ONLY a JSON array of sub-questions, nothing else

Example:
Question: "Compare Apple and Microsoft revenue growth from 2021 to 2023"
Output: [
  "What was Apple total revenue in 2021 2022 and 2023?",
  "What was Microsoft total revenue in 2021 2022 and 2023?",
  "What factors did Apple cite for revenue changes in their 10-K filings?",
  "What factors did Microsoft cite for revenue changes in their 10-K filings?"
]"""


def planner_node(state: AgentState) -> AgentState:
    question = state["original_question"]
    retry    = state.get("retry_count", 0)

    print(f"\n[PLANNER] Decomposing question (attempt {retry + 1})...")
    print(f"  Question: {question}")

    try:
        response = llm.invoke([
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=f"Decompose this question: {question}")
        ])

        raw    = response.content.strip()
        raw    = raw.replace("```json", "").replace("```", "").strip()
        sub_qs = json.loads(raw)

        print(f"  Generated {len(sub_qs)} sub-questions:")
        for i, q in enumerate(sub_qs):
            print(f"    {i+1}. {q}")

        return {
            **state,
            "sub_questions": sub_qs
        }

    except Exception as e:
        print(f"  [PLANNER ERROR] {e}")
        return {
            **state,
            "sub_questions": [question],
            "error":         str(e)
        }