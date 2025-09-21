# inspect_db.py
import chromadb
from chromadb.config import Settings

DB_DIR = "chroma_db"
client = chromadb.Client(Settings(persist_directory=DB_DIR))
collection = client.get_or_create_collection(name="sparkle_evidence")

res = collection.get(include=["documents", "metadatas"])
print(f"Total chunks: {len(res['documents'])}")

for i, (doc, meta) in enumerate(zip(res["documents"], res["metadatas"]), start=1):
    print(f"\nChunk {i}:")
    print(f"Source: {meta.get('source')}")
    print(f"Metadata: {meta}")
    print(f"Preview: {doc[:300]}...")
