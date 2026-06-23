# SoulSpace 🌌

SoulSpace is an AI-powered mental wellness companion designed for students.

At its core is **Seren**, a supportive conversational AI that helps students reflect on their thoughts, manage stress, and access evidence-based mental health resources in a safe and encouraging environment.

The platform combines:

* 💬 AI Mental Health Companion (Seren)
* 🧠 MBTI Personality Assessment
* 📊 PHQ-9 Depression Screening
* 🌱 GAD-7 Anxiety Screening
* 📚 Retrieval-Augmented Generation (RAG) knowledge base
* 🗄️ Persistent user test history
* 🔐 Secure authentication system

---

## Features

### Seren AI Chatbot

Seren uses Large Language Models together with Retrieval-Augmented Generation (RAG) to provide:

* Personalized conversations
* Mental wellness guidance
* Study and stress-management support
* Context-aware responses based on assessment history

### Mental Health Assessments

#### MBTI Personality Test

Provides personality insights and learning recommendations.

#### PHQ-9

Evidence-based depression screening questionnaire.

#### GAD-7

Evidence-based anxiety screening questionnaire.

Assessment results are stored and used to provide personalized AI responses.

---

## Technology Stack

### Backend

* Flask
* SQLite
* ChromaDB
* Sentence Transformers
* OpenRouter API

### Frontend

* HTML
* CSS
* JavaScript

### AI & RAG

* OpenRouter LLMs
* SentenceTransformer embeddings
* ChromaDB vector database

---

## Project Structure

```text
SoulSpace/
│
├── app.py
├── requirements.txt
├── sparkle.env
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── homepage.html
│   ├── mbti.html
│   ├── phq-9.html
│   └── gad-7.html
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── videos/
│
├── chroma_db/
│
└── soulspace.db
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/SoulSpace.git
cd SoulSpace
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a file named:

```text
sparkle.env
```

Add:

```env
SECRET_KEY=your_secret_key

OPENROUTER_API_KEY=your_openrouter_api_key

OPENROUTER_MODEL=x-ai/grok-4-fast:free
```

---

## Running the Application

Start the Flask server:

```bash
flask run
```

or

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## Database

SoulSpace currently uses SQLite.

### users

Stores:

* User accounts
* Email addresses
* Password hashes

### test_results

Stores:

* MBTI results
* PHQ-9 scores
* GAD-7 scores
* Submission timestamps

The AI chatbot uses a user's assessment history to personalize responses.

---

## Future Roadmap

* Google OAuth Login
* Counselor Escalation System
* Risk Detection Engine
* Wellness Analytics Dashboard
* Student Progress Tracking
* Admin & Counselor Portal
* Enhanced RAG Knowledge Base

---

## Disclaimer

SoulSpace is designed as a mental wellness support tool and educational companion.

It is not a substitute for professional medical diagnosis, treatment, or emergency mental health services.
