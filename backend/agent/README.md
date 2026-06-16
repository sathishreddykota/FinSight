# FinSight — Agentic Finance Research Assistant

> Multi-hop RAG system that answers complex financial questions by autonomously
> decomposing queries, retrieving from SEC 10-K filings, and synthesizing
> grounded, cited answers.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-1.2-green)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![Qdrant](https://img.shields.io/badge/Qdrant-1.18-red)

---

## What it does

Most RAG systems fail at complex questions like:

> *"Compare Apple and Microsoft revenue growth from 2021–2023 and explain
> what drove the difference"*

This requires retrieving from multiple documents, across multiple companies
and years, then reasoning across all of them. FinSight solves this with an
**agentic multi-hop retrieval pipeline**.

---

## Architecture

---

## Knowledge Base

| Company | Ticker | Documents | Years |
|---------|--------|-----------|-------|
| Apple | AAPL | 10-K Annual Reports | 2021, 2022, 2023 |
| Microsoft | MSFT | 10-K Annual Reports | 2021, 2022, 2023 |
| Google | GOOGL | 10-K Annual Reports | 2021, 2022, 2023 |
| Meta | META | 10-K Annual Reports | 2021, 2022, 2023 |
| Amazon | AMZN | 10-K Annual Reports | 2021, 2022, 2023 |

- **15 SEC filings** downloaded directly from SEC EDGAR
- **21,762 chunks** indexed with 384-dim embeddings
- **Vector DB:** Qdrant (cosine similarity)
- **Embedding model:** BAAI/bge-small-en-v1.5

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent framework | LangGraph |
| LLM | Llama 3.3 70B via Groq |
| Embeddings | BAAI/bge-small-en-v1.5 (FastEmbed) |
| Vector DB | Qdrant |
| Reranker | FlashRank (ms-marco-MiniLM-L-12-v2) |
| Backend | FastAPI + Uvicorn |
| Frontend | Next.js 16 + TypeScript + Tailwind |
| Data source | SEC EDGAR (sec-edgar-downloader) |

---

## Sample Questions

---

## Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop

### 1. Clone and setup

```bash
git clone https://github.com/yourusername/finsight.git
cd finsight
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Environment variables

```bash
cp .env.example .env
# Add your API keys to .env
```

### 3. Start Qdrant

```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

### 4. Ingest data

```bash
python backend/ingestion/sec_scraper.py
python backend/ingestion/chunker.py
python backend/ingestion/indexer.py
```

### 5. Start backend

```bash
uvicorn backend.api.main:app --reload --port 8000
```

### 6. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

---

## Key Design Decisions

**Why agentic retrieval over single-shot RAG?**
Complex financial questions require evidence from multiple documents. Single-shot
RAG retrieves once and misses cross-document relationships. The agent loop
retrieves iteratively until the judge confirms sufficient context.

**Why FlashRank over API-based rerankers?**
FlashRank runs locally with no API cost, zero latency overhead from network
calls, and no vendor dependency. The ms-marco model is well-proven for
passage reranking.

**Why LangGraph over vanilla LangChain?**
LangGraph gives explicit control over the agent state machine — the retry
loop, conditional edges, and state passing between nodes are all transparent
and debuggable. No magic.

---

## Resume Bullet Point

> Built FinSight, an agentic multi-hop RAG system over 15 SEC 10-K filings
> (21,762 chunks) using LangGraph, Qdrant, and FlashRank — achieving
> cross-document financial reasoning with automatic query decomposition,
> sufficiency evaluation, and cited answer synthesis.

---

## Author

**Sathi** · [GitHub](https://github.com/yourusername) ·
[LinkedIn](https://linkedin.com/in/yourusername)

> ⚠️ Not financial advice. For educational and portfolio purposes only.