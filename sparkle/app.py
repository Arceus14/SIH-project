import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect

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

def ensure_history():
    """Initialize conversation history if not present."""
    if "history" not in session:
        session["history"] = [{"role": "system", "content": SYSTEM_PROMPT}]

def get_ai_reply(messages):
    """Send the conversation history to the AI and return its reply."""
    payload = {
        "model": "deepseek/deepseek-chat-v3.1:free",
        "messages": messages
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        data = r.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return "Sorry, I couldn't process that."
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def index():
    ensure_history()
    return render_template('index.html', history=session["history"])

@app.route('/new')
def new_chat():
    session.pop("history", None)  # Clear conversation
    return redirect('/')


@app.route('/submit', methods=['POST'])
def submit():
    ensure_history()
    user_message = request.form['prompt']

    # Add user message
    session["history"].append({"role": "user", "content": user_message})

    # Get AI reply
    ai_reply = get_ai_reply(session["history"])

    # Add AI reply
    session["history"].append({"role": "assistant", "content": ai_reply})
    session.modified = True

    return render_template('index.html', history=session["history"])


'''@app.route('/mbti',methods=["POST"])
def mbti():'''







if __name__ == '__main__':
    app.run(debug=True)
