# backend/ingestion/test_search.py

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from fastembed import TextEmbedding

load_dotenv()

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "finsight")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

client   = QdrantClient(url="http://localhost:6333")
embedder = TextEmbedding(EMBEDDING_MODEL)

# Check collection
info  = client.get_collection(COLLECTION_NAME)
print(f"✅ Collection: {COLLECTION_NAME}")
print(f"✅ Total vectors: {info.points_count}")

# Test search
query     = "Apple revenue growth"
query_vec = list(embedder.embed([query]))[0].tolist()

results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vec,
    limit=3
).points

print(f"\nTest query: '{query}'")
print(f"Top 3 results:\n")

for i, r in enumerate(results):
    print(f"Result {i+1}:")
    print(f"  Company: {r.payload.get('company')}")
    print(f"  Year:    {r.payload.get('year')}")
    print(f"  Score:   {r.score:.4f}")
    print(f"  Text:    {r.payload.get('text', '')[:200]}...")
    print()