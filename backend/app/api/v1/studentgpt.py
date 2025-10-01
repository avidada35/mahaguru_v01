from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import asyncio

# Import StudentGPT inference from local package. Using relative project path (no 'backend.' prefix)
from studentgpt.inference import studentgpt_chat
from app.core.config import settings

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message for StudentGPT")


class ChatResponse(BaseModel):
    response: str


@router.get("/health")
async def health_check():
    """Health check endpoint for StudentGPT service."""
    # In dev mode with StudentGPT disabled, still report ok (service reachable)
    if settings.STUDENTGPT_DISABLED or settings.DEV_MODE:
        return {"status": "ok", "dev_mode": True}
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint that processes messages through StudentGPT.

    - Respects DEV_MODE/STUDENTGPT_DISABLED by returning mock responses.
    - Applies timeout via settings.STUDENTGPT_TIMEOUT_SECONDS.
    """
    # Dev mode or explicitly disabled: return a quick mock without loading models
    if settings.STUDENTGPT_DISABLED or settings.DEV_MODE:
        return ChatResponse(response=f"[DEV MODE] Echo: {request.message}")

    try:
        # Timeout wrapper for model inference
        async def run_inference():
            return await asyncio.to_thread(studentgpt_chat, request.message)

        response = await asyncio.wait_for(
            run_inference(), timeout=settings.STUDENTGPT_TIMEOUT_SECONDS
        )
        return ChatResponse(response=response)
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="StudentGPT inference timed out",
        )
    except Exception as e:
        # Avoid leaking internals; log details server-side, return generic error
        raise HTTPException(
            status_code=500,
            detail="StudentGPT inference error",
        )
