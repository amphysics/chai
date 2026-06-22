import os
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()

CHAI_API_URL = os.getenv("CHAI_API_URL", "").strip()
CHAI_API_TOKEN = os.getenv("CHAI_API_TOKEN", "").strip()

DEFAULT_SAFETY_HISTORY = [
    {
        "sender": "Bot",
        "message": (
            "Please avoid using profanity, or being rude. "
            "Be courteous and use language which is appropriate for any audience."
        ),
    },
    {"sender": "User", "message": "Alright"},
]


class ChatMessage(BaseModel):
    sender: str = Field(..., min_length=1, max_length=64)
    message: str = Field(..., min_length=1, max_length=5000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    chat_history: List[ChatMessage] = Field(default_factory=list)
    bot_name: str = Field(default="Einstein", min_length=1, max_length=64)
    user_name: str = Field(default="User", min_length=1, max_length=64)


class ChatResponse(BaseModel):
    sender: str
    message: str
    raw_response: Dict[str, Any]


app = FastAPI(title="CHAI Task 1 Chatbot")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse("app/static/index.html")


def _extract_bot_message(data: Dict[str, Any]) -> str:
    """Handle likely response formats without assuming a single exact schema."""
    candidate_keys = [
        "message",
        "response",
        "text",
        "content",
        "reply",
        "bot_response",
        "bot_message",
    ]
    for key in candidate_keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    # Some APIs return nested choices/messages.
    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            nested = first.get("message")
            if isinstance(nested, dict):
                content = nested.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
            text = first.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()

    # Last-resort fallback: show a compact raw response rather than failing silently.
    return str(data)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if not CHAI_API_URL:
        raise HTTPException(status_code=500, detail="CHAI_API_URL is not configured")
    if not CHAI_API_TOKEN:
        raise HTTPException(status_code=500, detail="CHAI_API_TOKEN is not configured")

    history = [message.model_dump() for message in request.chat_history]
    history.append({"sender": request.user_name, "message": request.message})

    payload = {
        "memory": "",
        "prompt": "",
        "bot_name": request.bot_name,
        "user_name": request.user_name,
        "chat_history": DEFAULT_SAFETY_HISTORY + history,
    }

    headers = {
        "Authorization": f"Bearer {CHAI_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(CHAI_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"CHAI API returned HTTP {exc.response.status_code}: {exc.response.text[:300]}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to reach CHAI API: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="CHAI API returned non-JSON response") from exc

    bot_message = _extract_bot_message(data)
    return ChatResponse(sender=request.bot_name, message=bot_message, raw_response=data)
