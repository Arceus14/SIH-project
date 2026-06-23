import os, uuid
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request,
    session, redirect, url_for,
    jsonify, g, flash
)
from werkzeug.security import (
    generate_password_hash, check_password_hash
)
from dotenv import load_dotenv

# New for RAG
import requests
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# --------------------
# App + Env setup
# --------------------
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY missing in sparkle.env")

OPENROUTER_URL  = "https://openrouter.ai/api/v1/chat/completions"
HEADERS         = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
MODEL_NAME      = os.getenv("OPENROUTER_MODEL", "x-ai/grok-4-fast")

SYSTEM_PROMPT = (
     "You are Seren , a student companion that aims to assist students in maintaining a good mindset. "
    "Your main goal is to make sure the student interacting with you is uplifted, energized, and free from mental stress, "
    "trauma, career stress, and academic pressure. You assist them with their career goals. "
    "You keep the conversation light and uplifting. Use simple words. "
    "Keep replies short and sweet."
    "Maintain quirky humour."
    "Never encourage negative thoughts like suicide or self-harm. "
    "In the beginning, display a positive or funny/sarcastic quote and greet only once. "
    "Keep the tone simple and don't mention negative emotions unless the student brings them up."

)

# --------------------
# Database (SQLite)
# --------------------
DB_PATH = os.getenv("SOULSPACE_DB", "soulspace.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = get_db()
    # users table
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # test_results table
    db.execute("""
    CREATE TABLE IF NOT EXISTS test_results (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT NOT NULL,
      test_type TEXT NOT NULL,      -- 'MBTI','PHQ9','GAD7'
      result TEXT NOT NULL,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    db.commit()

# Initialize the database once at startup
with app.app_context():
    init_db()


# --------------------
# Test-result helpers
# --------------------
def add_test_result(user_id, test_type, result):
    db = get_db()
    db.execute(
        "INSERT INTO test_results (user_id,test_type,result) VALUES (?,?,?)",
        (user_id, test_type, result)
    )
    db.commit()

def get_test_history(user_id, test_type):
    rows = get_db().execute("""
      SELECT result, timestamp
      FROM test_results
      WHERE user_id=? AND test_type=?
      ORDER BY timestamp
    """, (user_id, test_type)).fetchall()
    return [{"result": r["result"], "timestamp": r["timestamp"]} for r in rows]

def get_all_histories(user_id):
    return {
      "MBTI": get_test_history(user_id, "MBTI"),
      "PHQ9": get_test_history(user_id, "PHQ9"),
      "GAD7": get_test_history(user_id, "GAD7")
    }

def format_history(hist):
    if not hist:
        return "none"
    return ", ".join(f"{h['result']} ({h['timestamp']})" for h in hist)

# --------------------
# RAG retrieval setup
# --------------------
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embedder    = SentenceTransformer(EMBED_MODEL)
client      = chromadb.PersistentClient(path="chroma_db", settings=Settings(allow_reset=False))
collection  = client.get_collection("docs")

def retrieve_chunks(query, top_k=4):
    vec     = embedder.encode([query], convert_to_numpy=True).tolist()
    results = collection.query(
      query_embeddings=vec, n_results=top_k,
      include=["documents"]
    )
    return results.get("documents", [[]])[0]

# --------------------
# AI call
# --------------------
def get_ai_reply(messages):
    payload = {"model": MODEL_NAME, "messages": messages}
    try:
        r    = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=30)
        data = r.json()
        if r.status_code != 200:
            return f"API error: {data.get('error') or data}"
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {e}"

# --------------------
# Chat history & system prompt
# --------------------
def ensure_history():
    if "history" not in session:
        user_id = session["user_id"]
        h       = get_all_histories(user_id)
        prompt  = (
            SYSTEM_PROMPT
            + "\n\nYour test histories:\n"
            f"- MBTI: {format_history(h['MBTI'])}\n"
            f"- PHQ-9: {format_history(h['PHQ9'])}\n"
            f"- GAD-7: {format_history(h['GAD7'])}\n"
        )
        session["history"] = [{"role": "system", "content": prompt}]

# --------------------
# HTML page routes
# --------------------
@app.route("/")
def index():

    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())

    ensure_history()

    return render_template(
        "index.html",
        history=session.get("history", [])
    )

@app.route("/homepage")

def homepage():
    return render_template("homepage.html")

@app.route("/mbti")

def mbti():
    return render_template("mbti.html")

@app.route("/phq-9")

def phq9():
    return render_template("phq-9.html")

@app.route("/gad-7")

def gad7():
    return render_template("gad-7.html")

# --------------------
# Chat & test endpoints
# --------------------
@app.route("/submit", methods=["POST"])

def submit():
    user_id      = session["user_id"]
    user_message = request.form["prompt"]

    # Always fetch fresh test results
    histories = get_all_histories(user_id)
    test_summary = (
        f"- MBTI: {format_history(histories['MBTI'])}\n"
        f"- PHQ-9: {format_history(histories['PHQ9'])}\n"
        f"- GAD-7: {format_history(histories['GAD7'])}\n"
    )

    chunks  = retrieve_chunks(user_message)
    context = "\n\n".join(chunks)

    # Updated system message includes current tests
    system_msg = {
        "role": "system",
        "content": (
            "You are Seren — a warm, encouraging mental-health companion.\n\n"
            "The following are the user's **latest test histories**:\n"
            f"{test_summary}\n\n"
            "Use this data rigorously to look out for warning signs. "
            "If the PHQ-9 or GAD-7 scores suggest severe depression or anxiety, "
            "gently advise reaching out to a school counsellor. "
            "Do NOT diagnose, but do flag and escalate serious issues with supportive language.\n\n"
            "Also, below is some evidence context, use it to enhance your responses."
            "EVIDENCE CONTEXT:\n" + context
        )
    }

    # Construct message list fresh each time
    messages = [system_msg] + session.get("history", []) + [
        {"role": "user", "content": user_message}
    ]

    ai_reply = get_ai_reply(messages)

    # Store conversation
    if "history" not in session:
        session["history"] = []
    session["history"].append({"role": "user", "content": user_message})
    session["history"].append({"role": "assistant", "content": ai_reply})
    session.modified = True

    return render_template("index.html", history=session["history"])

# --------------------
# Test submission with AI feedback
# --------------------
@app.route("/submit_mbti", methods=["POST"])

def submit_mbti():
    print("=== MBTI Submit Triggered ===")
    user_id = session.get("user_id")
    mbti_type = request.form.get("mbti_type")
    print("Received MBTI type:", mbti_type)

    if not mbti_type:
        flash("Please complete the MBTI test before submitting.")
        return redirect(url_for("mbti"))

    # Store MBTI result in DB
    result = f"type={mbti_type}"
    add_test_result(user_id, "MBTI", result)
    print("Stored MBTI in DB:", result)

    # AI reply
    ensure_history()
    messages = session["history"] + [
        {"role": "user", "content": f"My MBTI result is {mbti_type}. "
                                    f"Please explain what this means in short and give uplifting, positive advice."}
    ]

    ai_reply = get_ai_reply(messages)
    session["history"].append({"role": "assistant", "content": ai_reply})
    session.modified = True
    print("AI reply appended to session history")

    return redirect(url_for("index"))


@app.route("/submit_phq9", methods=["POST"])

def submit_phq9():
    print("=== PHQ-9 Submit Triggered ===")  # debug
    user_id = session.get("user_id")
    print("User ID:", user_id)

    answers_raw = request.form.get("answers")
    print("Raw answers from form:", answers_raw)

    answers = []
    total = 0

    if answers_raw:
        try:
            import json
            answers = json.loads(answers_raw)
            total = sum(int(x) for x in answers)
            print("Parsed answers:", answers)
            print("Calculated total:", total)
        except Exception as e:
            print("Error parsing answers:", e)
            answers = [0]*9
            total = sum(answers)
            print("Fallback answers:", answers)
    else:
        print("No answers received, using default zeros")
        answers = [0]*9
        total = 0

    result = f"total={total}, answers={answers}"
    print("Result string to store:", result)
    add_test_result(user_id, "PHQ9", result)
    print("Stored test result in DB")

    # Add AI reply
    ensure_history()
    messages = session["history"] + [
        {"role": "user", "content": f"My PHQ-9 score is {total}. Please explain what this means in short and give uplifting advice."}
    ]
    print("Messages to AI:", messages)

    ai_reply = get_ai_reply(messages)
    print("AI reply received:", ai_reply)

    session["history"].append({"role": "assistant", "content": ai_reply})
    session.modified = True
    print("AI reply appended to session history")

    return redirect(url_for("index"))



@app.route("/submit_gad7", methods=["POST"])

def submit_gad7():
    print("=== GAD-7 Submit Triggered ===")
    user_id = session.get("user_id")

    answers_raw = request.form.get("answers")
    print("Raw answers from form:", answers_raw)

    answers = []
    total = 0

    if answers_raw:
        try:
            import json
            answers = json.loads(answers_raw)
            total = sum(int(x) for x in answers)
            print("Parsed answers:", answers)
            print("Calculated total:", total)
        except Exception as e:
            print("Error parsing answers:", e)
            answers = [0] * 7
            total = 0
    else:
        print("No answers received, using default zeros")
        answers = [0] * 7
        total = 0

    result = f"total={total}, answers={answers}"
    print("Result string to store:", result)
    add_test_result(user_id, "GAD7", result)
    print("Stored GAD-7 in DB")

    # Add AI reply
    ensure_history()
    messages = session["history"] + [
        {"role": "user", "content": f"My GAD-7 score is {total}. "
                                    f"Please explain what this means in short and give supportive advice."}
    ]
    print("Messages to AI:", messages)

    ai_reply = get_ai_reply(messages)
    print("AI reply received:", ai_reply)

    session["history"].append({"role": "assistant", "content": ai_reply})
    session.modified = True
    print("AI reply appended to session history")

    return redirect(url_for("index"))

def ensure_history():
    if "history" not in session:

        session["history"] = [{
            "role": "system",
            "content": SYSTEM_PROMPT
        }]

if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    app.run(debug=True)
