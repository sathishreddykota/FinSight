# backend/ingestion/indexer.py

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
# NEW
from qdrant_client.models import (
    Distance, VectorParams, PointStruct
)
from fastembed import TextEmbedding
import uuid

load_dotenv()

# Config
CHUNKS_PATH     = Path("data/processed/chunks.jsonl")
QDRANT_URL      = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "finsight")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
BATCH_SIZE      = 100  # upload 100 chunks at a time
VECTOR_SIZE     = 384  # bge-small-en-v1.5 output dimension


def load_chunks() -> list[dict]:
    """Load all chunks from JSONL file."""
    chunks = []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_PATH}")
    return chunks


def setup_collection(client: QdrantClient):
    """Create Qdrant collection if it doesn't exist."""
    existing = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME in existing:
        print(f"Collection '{COLLECTION_NAME}' already exists — deleting and recreating...")
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )
    print(f"✅ Collection '{COLLECTION_NAME}' created")


def index_chunks(chunks: list[dict], client: QdrantClient, embedder: TextEmbedding):
    """Embed all chunks and upload to Qdrant in batches."""
    total    = len(chunks)
    uploaded = 0

    print(f"\nIndexing {total} chunks in batches of {BATCH_SIZE}...\n")

    for batch_start in range(0, total, BATCH_SIZE):
        batch       = chunks[batch_start: batch_start + BATCH_SIZE]
        texts       = [c["text"] for c in batch]

        # Generate embeddings
        embeddings  = list(embedder.embed(texts))

        # Build Qdrant points
        points = []
        for chunk, embedding in zip(batch, embeddings):
            point = PointStruct(
                id      = str(uuid.uuid4()),
                vector  = embedding.tolist(),
                payload = {
                    "text":     chunk["text"],
                    "chunk_id": chunk["id"],
                    **chunk["metadata"]
                }
            )
            points.append(point)

        # Upload batch
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )

        uploaded += len(batch)
        progress  = (uploaded / total) * 100
        print(f"  Progress: {uploaded}/{total} ({progress:.1f}%) ✅")

    return uploaded


def verify_index(client: QdrantClient):
    """Verify the collection has the right number of vectors."""
    info = client.get_collection(COLLECTION_NAME)
    count = info.points_count
    print(f"\n--- Index Verification ---")
    print(f"Collection:   {COLLECTION_NAME}")
    print(f"Total vectors: {count}")
    print(f"Vector size:  {VECTOR_SIZE}")

    # Quick test search
    print(f"\nRunning test search: 'Apple revenue growth'...")
    embedder = TextEmbedding(EMBEDDING_MODEL)
    query_vec = list(embedder.embed(["Apple revenue growth"]))[0].tolist()

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=3
    )

    print(f"Top 3 results:")
    for i, r in enumerate(results):
        print(f"\n  Result {i+1}:")
        print(f"  Company: {r.payload.get('company')}")
        print(f"  Year:    {r.payload.get('year')}")
        print(f"  Score:   {r.score:.4f}")
        print(f"  Text:    {r.payload.get('text', '')[:150]}...")


if __name__ == "__main__":
    print("=== FinSight Indexer ===\n")

    # Connect to Qdrant
    print(f"Connecting to Qdrant at {QDRANT_URL}...")
    client = QdrantClient(url=QDRANT_URL)
    print("✅ Connected\n")

    # Load embedding model
    print(f"Loading embedding model: {EMBEDDING_MODEL}...")
    embedder = TextEmbedding(EMBEDDING_MODEL)
    print("✅ Model loaded\n")

    # Load chunks
    chunks = load_chunks()

    # Setup collection
    setup_collection(client)

    # Index everything
    total_uploaded = index_chunks(chunks, client, embedder)

    print(f"\n✅ Indexing complete! {total_uploaded} vectors uploaded to Qdrant")

    # Verify
    verify_index(client)