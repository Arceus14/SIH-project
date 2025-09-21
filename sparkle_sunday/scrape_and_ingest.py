#!/usr/bin/env python3
import os
import sys
import time
import uuid
import requests
from collections import deque
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# -------------------
# Safe HF cache setup
# -------------------
def first_writable(paths):
    for p in paths:
        try:
            os.makedirs(p, exist_ok=True)
            test = os.path.join(p, ".write_test")
            with open(test, "w") as f: f.write("ok")
            os.remove(test)
            return p
        except Exception:
            continue
    fallback = os.path.join(os.getcwd(), "hf_cache")
    os.makedirs(fallback, exist_ok=True)
    return fallback

SAFE_CACHE_DIR = first_writable([os.path.join(os.getcwd(), "hf_cache"), "/tmp/hf_cache"])
os.environ["HF_HOME"] = SAFE_CACHE_DIR
os.environ.pop("TRANSFORMERS_CACHE", None)
print(f"[HF] Using cache dir: {SAFE_CACHE_DIR}")



# -------------------
# Configuration
# -------------------
URLS = [
    # ── Indian student-focused portals ────────────────────────────────────────────
    "https://telemanas.mohfw.gov.in/",                                           # Tele MANAS (MoHFW helpline)
    "https://manodarpan.education.gov.in/",                                      # Manodarpan (MoE student support)
    "https://ntf.education.gov.in/",                                             # National Task Force on Student Mental Health
    "https://nhp.gov.in/healthlyliving/mental-health",                           # NHP mental-health advisory
    "https://nimhans.ac.in/centre-for-well-being",                               # NIMHANS Centre for Well-Being
    "https://aiims.edu/en/departments-and-centers/department-of-psychiatry.html", # AIIMS Dept. of Psychiatry
    "https://aiims.edu/en/departments-and-centers/centre-for-community-mental-health.html", # AIIMS CCMH
    "https://aiims.edu/en/departments-and-centers/centre-for-integrative-health-and-research.html", # AIIMS CIHR
    "https://icallhelpline.org/",                                                 # TISS-iCALL helpline
    "https://sangath.in/",                                                        # Sangath adolescent & student programs
    "https://mind.org.in/",                                                       # Mind India workshops/toolkits
    "https://www.livelovelaugh.org/",                                             # Live Love Laugh guides
    "https://www.cbse.gov.in/student-support-services",                           # CBSE Student Support Services
    "https://nta.ac.in/student-services",                                         # NTA Student Services & advisories
    "https://ncert.nic.in/life-skills-education",                                 # NCERT Life Skills Education

    # ── Global student-wellbeing authorities ────────────────────────────────────
    "https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response",
    "https://www.cdc.gov/mentalhealth/learn/index.htm",
    "https://www.nih.gov/health-topics/mental-health",
    "https://www.nhs.uk/mental-health/",
    "https://www.apa.org/topics/student-mental-health",
    "https://www.mentalhealth.gov/",
    "https://www.unicef.org/stories?topics=adolescent-mental-health",
    "https://www.beyondblue.org.au/get-support/students"
]


DB_DIR      = "chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 120
CONNECT_TIMEOUT       = 10
READ_TIMEOUT          = 60

# -------------------
# Helpers: fetch, parse, chunk
# -------------------
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; IngestionBot/1.0)"
})

def is_html(url):
    try:
        r = SESSION.head(url, allow_redirects=True, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        ct = r.headers.get("Content-Type", "")
        return "html" in ct.lower()
    except Exception:
        return False

def fetch_html(url):
    try:
        r = SESSION.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"⚠️  Fetch error {url}: {e}")
        return ""

def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","noscript","header","footer","nav","aside"]):
        tag.decompose()
    text = soup.get_text("\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)

def chunk_text(text):
    if not text:
        return []
    chunks, start, n = [], 0, len(text)
    while start < n:
        end = min(start + CHUNK_SIZE, n)
        chunk = text[start:end].strip()
        if len(chunk) >= max(100, CHUNK_SIZE // 3):
            chunks.append(chunk)
        if end == n:
            break
        start = end - CHUNK_OVERLAP
    return chunks

# -------------------
# Setup embeddings & Chroma
# -------------------
print(f"[Embeddings] Loading model {EMBED_MODEL}")
embedder = SentenceTransformer(EMBED_MODEL)

os.makedirs(DB_DIR, exist_ok=True)
client = chromadb.PersistentClient(path=DB_DIR, settings=Settings(allow_reset=False))
try:
    collection = client.get_collection("docs")
except:
    collection = client.create_collection("docs")

# -------------------
# Full-domain crawl + ingest
# -------------------
def crawl_and_ingest(base_url):
    domain = urlparse(base_url).netloc
    frontier = deque([base_url])
    visited = set()

    while True:
        if not frontier:
            break

        url = frontier.popleft()
        if url in visited:
            continue
        visited.add(url)

        if not is_html(url):
            continue

        print(f"🔍 Processing {url}")
        html = fetch_html(url)
        if not html:
            continue

        text = html_to_text(html)
        chunks = chunk_text(text)
        if chunks:
            embeddings = embedder.encode(chunks, convert_to_numpy=True).tolist()
            ids      = [str(uuid.uuid4()) for _ in chunks]
            metas    = [{"source": url} for _ in chunks]
            collection.upsert(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metas,
            )
            print(f"✅ Ingested {len(chunks)} chunks from {url}")

        # discover new links
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"].split("#")[0])
            parsed = urlparse(href)
            if parsed.scheme.startswith("http") and parsed.netloc.endswith(domain):
                if href not in visited:
                    frontier.append(href)

    print(f"🏁 Finished crawl for {base_url}, visited {len(visited)} pages.")

def main():
    start = time.perf_counter()
    for u in URLS:
        crawl_and_ingest(u)
    try:
        client.persist()  # ensure on-disk save
    except:
        pass
    total = time.perf_counter() - start
    print(f"\n--- All done in {total:.2f}s ---")
    print(f"DB stored at {os.path.abspath(DB_DIR)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(1)
