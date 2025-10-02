import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize the client
client = genai.Client(api_key=GEMINI_API_KEY)

# System prompt for Classroom AI
CLASSROOM_SYSTEM_PROMPT = """You are a good mentor and teacher. You are helping students learn and understand concepts in a classroom setting."""

async def generate_classroom_response(
    user_message: str, 
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate a response using Gemini API for classroom interactions
    
    Args:
        user_message: The user's question/message
        conversation_history: Optional list of previous messages
    
    Returns:
        str: Generated response from the AI
    """
    try:
        # Build conversation context
        conversation_context = ""
        if conversation_history:
            for msg in conversation_history[-5:]:  # Keep last 5 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                conversation_context += f"{role.capitalize()}: {content}\n"
        
        # Combine system prompt with conversation context and user message
        full_prompt = f"{CLASSROOM_SYSTEM_PROMPT}\n\n"
        if conversation_context:
            full_prompt += f"Previous conversation:\n{conversation_context}\n"
        full_prompt += f"Student: {user_message}\n\nTeacher:"
        
        print(f"[CLASSROOM] Processing query: {user_message[:100]}...")
        
        # Generate response using the new client-based approach
        response = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-2.0-flash-001',  # Using the latest model
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000
            )
        )
        
        if response and response.text:
            generated_text = response.text.strip()
            print(f"[CLASSROOM] Response generated successfully")
            return generated_text
        else:
            print("[CLASSROOM] Empty response from Gemini API")
            return "I apologize, but I couldn't generate a proper response. Could you please rephrase your question?"
            
    except Exception as e:
        print(f"[CLASSROOM] Error generating response: {str(e)}")
        return "I'm experiencing some technical difficulties right now. Please try again in a moment, or rephrase your question."

def format_response_with_metadata(bot_message: str) -> Dict[str, Any]:
    """
    Format the response with additional metadata
    
    Args:
        bot_message: The generated response text
    
    Returns:
        Dict containing formatted response data
    """
    return {
        "bot_message": bot_message,
        "timestamp": datetime.utcnow(),
        "success": True,
        "source": "gemini-2.0-flash-001"
    }
