# detectors.py
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# --- Logging setup ---
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO in production
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- Config ---
DB_DIR = "chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.6  # Adjust after testing

# --- Init ---
embedder = SentenceTransformer(EMBED_MODEL)
client = chromadb.Client(Settings(persist_directory=DB_DIR))
collection = client.get_or_create_collection(name="sparkle_evidence")

def is_mental_health_query(query: str) -> bool:
    """
    Dynamically decides if a query is mental-health-related
    by comparing it to your vector DB content tagged as 'mental_health'.
    """

    logging.debug(f"User query: {query}")

    # Embed the query
    q_emb = embedder.encode([query], normalize_embeddings=True)[0]

    # Search the DB for the closest chunk
    res = collection.query(
        query_embeddings=[q_emb],
        n_results=1,
        include=["metadatas", "distances", "documents"]
    )

    if not res["documents"] or not res["documents"][0]:
        logging.debug("No matches found in vector DB.")
        return False

    # Chroma returns distance, so convert to similarity
    distance = res["distances"][0][0]
    similarity = 1 - distance
    meta = res["metadatas"][0][0]
    doc_preview = res["documents"][0][0][:150].replace("\n", " ")

    topic = meta.get("topic", "").lower() if meta else ""

    logging.debug(f"Top match preview: {doc_preview}...")
    logging.debug(f"Top match metadata: {meta}")
    logging.debug(f"Similarity score: {similarity:.3f}")
    logging.debug(f"Detected topic: {topic}")

    decision = (topic == "mental_health" or topic == "") and similarity >= SIMILARITY_THRESHOLD
    logging.debug(f"Decision: {'MENTAL HEALTH QUERY' if decision else 'NORMAL QUERY'}")

    return decision
