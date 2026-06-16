# backend/api/main.py

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.agent.graph import run_agent

app = FastAPI(
    title="FinSight API",
    description="Agentic RAG Financial Research Assistant",
    version="1.0.0"
)

# Allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question:      str
    answer:        str
    sources:       list[dict]
    sub_questions: list[str]
    retry_count:   int


@app.get("/")
def root():
    return {"status": "FinSight API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = run_agent(request.question)
        return QueryResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"],
            sub_questions=result["sub_questions"],
            retry_count=result["retry_count"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/companies")
def get_companies():
    return {
        "companies": [
            {"name": "Apple",     "ticker": "AAPL"},
            {"name": "Microsoft", "ticker": "MSFT"},
            {"name": "Google",    "ticker": "GOOGL"},
            {"name": "Meta",      "ticker": "META"},
            {"name": "Amazon",    "ticker": "AMZN"}
        ],
        "years": ["2021", "2022", "2023"]
    }