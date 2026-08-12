# LLM Assessment Agent

An end-to-end adaptive assessment system that tests your knowledge of Large Language Models. Built with **FastAPI** (Python) and **Next.js** (React).

## Features

- **Adaptive Difficulty** — Starts at beginner and progresses to expert as you answer correctly (3 consecutive correct = level up)
- **AI-Powered Q&A** — Uses OpenRouter (GPT-4o-mini) to generate questions and verify answers
- **Local Fallback** — Works without an API key using 20 curated questions across all difficulty levels
- **Dashboard** — Daily, weekly, and monthly performance with trend charts (Recharts)
- **Session Review** — Per-question breakdown, corrections, recommendations, weak/strong areas
- **Knowledge Graph** — Accuracy and difficulty progression over time

## Project Structure

```
llm-assessment/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── core/config.py           # Settings (API key, model, DB)
│   │   ├── core/database.py         # SQLite + SQLAlchemy
│   │   ├── models/schemas.py        # Database models
│   │   ├── models/pydantic_models.py # API schemas
│   │   ├── routers/
│   │   │   ├── sessions.py          # Session CRUD + review
│   │   │   ├── questions.py         # Question generation + verification
│   │   │   └── dashboard.py         # Stats + trends
│   │   └── services/
│   │       ├── openrouter.py        # OpenRouter API client
│   │       └── question_service.py  # Business logic + fallback questions
│   ├── .env                         # Environment variables
│   └── requirements.txt
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx                 # Home page
│   │   ├── api.ts                   # API client
│   │   ├── globals.css              # Dark theme
│   │   ├── assessment/[id]/page.tsx # Question/answer flow
│   │   ├── dashboard/page.tsx       # Charts + stats
│   │   └── review/[id]/page.tsx     # Session review
│   ├── package.json
│   └── tsconfig.json
└── start.sh                         # Launch both servers
```

## Prerequisites

- **Python 3.10+** (tested with 3.13)
- **Node.js 18+**
- **(Optional)** An [OpenRouter](https://openrouter.ai) API key for AI-powered question generation

## Setup

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Frontend

```bash
cd frontend
npm install
```

## Setting Up the LLM Key (OpenRouter)

OpenRouter generates dynamic questions and verifies your answers with explanations. Without it, the system uses a built-in question bank (20 questions across 4 difficulty levels).

1. Go to [openrouter.ai/keys](https://openrouter.ai/keys) and create a key
2. Open `backend/.env` and set your key:

```env
LLM_ASMT_OPENROUTER_API_KEY=sk-or-v1-your-key-here
LLM_ASMT_OPENROUTER_MODEL=openai/gpt-4o-mini
LLM_ASMT_DB_URL=sqlite:///./llm_assessment.db
LLM_ASMT_CORS_ORIGINS=http://localhost:3000
```

The `LLM_ASMT_` prefix avoids conflicts with other environment variables on your system.

To change the model, update `LLM_ASMT_OPENROUTER_MODEL` to any model available on OpenRouter (e.g., `anthropic/claude-3.5-sonnet`, `google/gemini-pro`).

## Running

### Start Both Servers

```bash
./start.sh
```

### Or Start Individually

**Backend** (http://localhost:8000):
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend** (http://localhost:3000):
```bash
cd frontend
npm run dev
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/sessions` | Create a new assessment session |
| GET | `/api/sessions` | List all sessions |
| GET | `/api/sessions/:id` | Get session summary |
| GET | `/api/sessions/:id/review` | Get session review with recommendations |
| DELETE | `/api/sessions/:id` | Delete a session |
| POST | `/api/questions/next/:session_id` | Get the next question |
| POST | `/api/questions/answer` | Submit an answer |
| GET | `/api/dashboard` | Get daily/weekly/monthly stats + trend |
| GET | `/api/health` | Health check |

## How the Assessment Works

1. **Start** a session — begins at **beginner** difficulty
2. **Answer** questions — each answer is verified against the correct answer
3. **Level up** — 3 consecutive correct answers advances to the next difficulty tier
4. **Complete** — the session ends after 5+ questions (when you get one wrong or reach 20 questions)
5. **Review** — see your results, corrections, and AI-generated learning recommendations
