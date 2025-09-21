# rag.py
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

DB_DIR = "chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

client = chromadb.Client(Settings(persist_directory=DB_DIR))
collection = client.get_or_create_collection(name="sparkle_evidence")
embedder = SentenceTransformer(EMBED_MODEL)



def retrieve_chunks(query, top_k=3):
    q_emb = embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
    res = collection.query(query_embeddings=[q_emb], n_results=top_k, include=["documents", "metadatas", "distances"])

    print("\n=== Retrieval Debug ===")
    print(f"Query: {query}")
    for i, (doc, meta, dist) in enumerate(zip(res["documents"][0], res["metadatas"][0], res["distances"][0]), start=1):
        sim = 1 - dist
        print(f"\nResult {i}:")
        print(f"Similarity: {sim:.3f}")
        print(f"Source: {meta.get('source')}")
        print(f"Metadata: {meta}")
        print(f"Preview: {doc[:300]}...")  # first 300 chars
    print("=======================\n")

    docs = res["documents"][0]
    metas = res["metadatas"][0]
    return [f"[{m['source']}] {d}" for d, m in zip(docs, metas)]
