from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging
from app.core.config import settings
from google import genai  # NEW SDK (google-genai)
# Initialize router
router = APIRouter()

# Initialize logger
logger = logging.getLogger(__name__)


# Pydantic Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message for Classroom/Manthan")


class ChatResponse(BaseModel):
    response: str


# Health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "ok"}


# Config check endpoint (useful for debugging)
@router.get("/config/check")
async def check_config():
    import os
    huggingface_api_key = getattr(settings, 'HUGGINGFACE_API_KEY', None)
    gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
    return {
        "huggingface_api_key_set": bool(huggingface_api_key),
        "huggingface_api_key_length": len(huggingface_api_key or ''),
        "huggingface_api_key_prefix": (huggingface_api_key[:8] + "...") if huggingface_api_key else "NOT SET",
        "gemini_api_key_set": bool(gemini_api_key),
        "gemini_api_key_length": len(gemini_api_key or ''),
        "gemini_api_key_prefix": (gemini_api_key[:8] + "...") if gemini_api_key else "NOT SET",
        "environment": os.getenv("ENV", "not set")
    }


# Core chat function
async def classroom_chat(message: str) -> str:
    """Chat using Google Gemini API (google-genai SDK)"""
    # Check if API key is configured
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured")
        raise RuntimeError("GEMINI_API_KEY not configured. Please add it to your .env file.")
    try:
        logger.info(f"Sending message to Gemini: {message[:100]}...")
        # Set API key in environment if not already set
        import os
        if not os.environ.get("GEMINI_API_KEY"):
            os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message
        )
        logger.info("Successfully received response from Gemini")
        return response.text or ""
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}", exc_info=True)
        raise RuntimeError(f"Gemini API error: {str(e)}")


# Chat endpoint
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to Gemini AI and get a response.
    """
    try:
        logger.info(f"Received classroom chat request: {request.message[:50]}...")
        
        # Get response from Gemini
        response = await classroom_chat(request.message)
        
        logger.info("Successfully generated response")
        
        return ChatResponse(response=response)
        
    except RuntimeError as e:
        logger.error(f"Runtime error in classroom chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error in classroom chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )