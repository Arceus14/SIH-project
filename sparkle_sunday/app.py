import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, jsonify

# NEW: imports for vector retrieval
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Load environment variables
load_dotenv("sparkle.env")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")  # Needed for session

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in sparkle.env")

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = (
    "You are Sparkle, a student companion that aims to assist students in maintaining a good mindset. "
    "Your main goal is to make sure the student interacting with you is uplifted, energized, and free from mental stress, "
    "trauma, career stress, and academic pressure. You assist them with their career goals. "
    "You keep the conversation light and uplifting. Use simple words and keep replies short and sweet. "
    "Never encourage negative thoughts like suicide or self-harm. "
    "In the beginning, display a positive or funny/sarcastic quote and greet only once. "
    "Keep the tone simple and don't mention negative emotions unless the student brings them up."
)

# ---------------------------
# NEW: Load embedder & Chroma
# ---------------------------
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embedder = SentenceTransformer(EMBED_MODEL)

DB_DIR = "chroma_db"
client = chromadb.PersistentClient(path=DB_DIR, settings=Settings(allow_reset=False))
collection = client.get_collection("docs")

def retrieve_chunks(query: str, top_k: int = 4):
    """Embed the query and retrieve top_k most relevant chunks from Chroma."""
    q_vec = embedder.encode([query], convert_to_numpy=True).tolist()
    results = collection.query(
        query_embeddings=q_vec,
        n_results=top_k,
        include=["documents", "metadatas"]
    )
    # Return just the text chunks
    test_chunks = results["documents"][0]
    print(f"These are results\n\n\n\n\n{test_chunks}")
    return results["documents"][0]

# ---------------------------

def ensure_history():
    if "history" not in session:
        system_prompt = SYSTEM_PROMPT
        if 'mbti_history' in session and session['mbti_history']:
            system_prompt += (
                " The user has previously had these MBTI results: "
                f"{format_mbti_history()}."
            )
        session["history"] = [{"role": "system", "content": system_prompt}]

def format_mbti_history():
    if 'mbti_history' not in session or not session['mbti_history']:
        return ""
    return ", ".join(
        f"{entry['type']} ({entry['timestamp']})"
        for entry in session['mbti_history']
    )

def get_ai_reply(messages):
    payload = {
        "model": "deepseek/deepseek-chat-v3.1:free",
        "messages": messages
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        print("AI API status:", r.status_code)
        data = r.json()
        print("AI API raw response:", data)

        if r.status_code != 200:
            err = data.get("error") or data
            return f"API error: {err}"

        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()

        return f"Unexpected API response shape: {data}"

    except Exception as e:
        print("Exception in get_ai_reply:", e)
        return f"Error when calling AI: {e}"

@app.route('/')
def index():
    ensure_history()
    return render_template('index.html', history=session["history"])

@app.route('/new')
def new_chat():
    session.pop("history", None)
    return redirect('/')

@app.route('/submit', methods=['POST'])
def submit():
    ensure_history()
    user_message = request.form['prompt']

    # Retrieve top chunks from Chroma
    chunks = retrieve_chunks(user_message, top_k=4)

    # DEBUG: log retrieved chunks
    print("\n--- Retrieved Chunks ---")
    if not chunks:
        print("No chunks retrieved!")
    else:
        for i, c in enumerate(chunks, 1):
            print(f"[{i}] {c[:200]}...\n")  # first 200 chars
    print("--- End Retrieved Chunks ---\n")

    context_block = "\n\n".join(chunks)

    # Build system message with context
    system_msg = {
        "role": "system",
        "content": (
            "You are Sparkle, a supportive, student‑focused mental‑health companion. "
            "You respond with empathy, clarity, and actionable guidance, while keeping a warm, encouraging tone.\n\n"
            "Below is the EVIDENCE content, if you find it relevant to the user prompt, use the EVIDENCE content to enhance and generate a helpful reply."
            "If the EVIDENCE content is not relevant, reply normally."
            "EVIDENCE CONTEXT:\n"
            f"{context_block}"
        )
    }

    # Build messages: system → history → current user query
    messages = [system_msg] + session["history"] + [{"role": "user", "content": user_message}]

    # DEBUG: log final prompt
    print("\n===== FINAL PROMPT SENT TO AI =====")
    for m in messages:
        print(f"{m['role'].upper()}:\n{m['content']}\n")
    print("===== END PROMPT =====\n")

    # Call AI
    ai_reply = get_ai_reply(messages)

    # Update session history
    session["history"].append({"role": "user", "content": user_message})
    session["history"].append({"role": "assistant", "content": ai_reply})
    session.modified = True

    return render_template('index.html', history=session["history"])

@app.route('/submit_mbti', methods=['POST'])
def submit_mbti():
    data = request.get_json()
    mbti_type = data.get('type')

    if not mbti_type:
        return jsonify({"status": "error", "message": "No MBTI type provided"}), 400

    if 'mbti_history' not in session:
        session['mbti_history'] = []

    session['mbti_history'].append({
        "type": mbti_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    ensure_history()

    try:
        all_types_str = format_mbti_history()
        ai_reply = get_ai_reply(session["history"] + [
            {
                "role": "user",
                "content": (
                    f"My latest MBTI result is {mbti_type}. "
                    f"My full MBTI history is: {all_types_str}. "
                    "Please acknowledge my latest MBTI and give healthy, positive advice."
                )
            }
        ])

        if ai_reply.startswith('"') and ai_reply.endswith('"'):
            ai_reply = ai_reply[1:-1]
    except Exception as e:
        app.logger.error(f"Error getting AI reply: {e}")
        ai_reply = None

    return jsonify({
        "status": "ok",
        "history": session['mbti_history'],
        "ai_reply": ai_reply or ""
    })

if __name__ == '__main__':
    app.run(debug=True)
