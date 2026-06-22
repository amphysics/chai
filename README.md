# CHAI Task 1 — Chatbot Interface

This is a small Task 1 implementation: a user can interact with a chatbot through a clean web UI backed by a Python FastAPI proxy.

The app intentionally keeps scope small and focused:

- simple chat interface
- Python backend wrapper around the CHAI model API
- message history preservation
- loading and error states
- environment-variable based API configuration
- no token hardcoding in frontend code

## Project structure

```text
chai_task1/
  app/
    main.py              # FastAPI backend and CHAI API client
    static/
      index.html         # Chat UI
      styles.css         # Styling
      app.js             # Frontend behavior
  .env.example           # Environment variable template
  requirements.txt
  README.md
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set:

```bash
CHAI_API_URL=<endpoint from assignment>
CHAI_API_TOKEN=<token from assignment>
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## Design notes

The browser never directly calls the CHAI model endpoint. Instead, it calls the local FastAPI backend at `/api/chat`. This keeps the bearer token out of frontend code and makes it easier to add validation, logging, retries, rate limiting, or auth later.

The backend keeps the API payload close to the assignment schema:

```json
{
  "memory": "",
  "prompt": "",
  "bot_name": "Einstein",
  "user_name": "User",
  "chat_history": [
    {"sender": "Bot", "message": "Please avoid using profanity, or being rude. Be courteous and use language which is appropriate for any audience."},
    {"sender": "User", "message": "Alright"},
    {"sender": "User", "message": "..."}
  ]
}
```

## Possible extensions

Given more time, I would add streaming UX, persisted conversations, auth, rate limiting, observability, and deployment through a small containerized service.
