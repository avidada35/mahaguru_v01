import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any
import asyncio
from datetime import datetime
from refiner_agent import refine_query

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

def classify_query(query: str) -> str:
    """
    Classifies the user query as 'simple' or 'complex'.
    Simple: Greetings, short queries, basic questions.
    Complex: Learning/upskilling requests, multi-step, or context-heavy queries.
    """
    greetings = [
        "hi", "hello", "hey", "thanks", "thank you",
        "good morning", "good evening", "good afternoon", "how are you"
    ]
    learning_keywords = [
        "learn", "study", "prepare", "exam", "explore", "upskill", "practice", 
        "improve", "understand", "help me with", "teach", "guide", "assignment", 
        "project", "syllabus", "topic", "explain", "how to", "want to", "need to"
    ]
    
    query_lower = query.strip().lower()
    
    print(f"\n{'='*70}")
    print(f"[CLASSIFIER] Analyzing query: '{query}'")
    print(f"[CLASSIFIER] Query length: {len(query_lower.split())} words")
    
    # Check for learning/upskilling intent FIRST (highest priority)
    matched_learning_keywords = [kw for kw in learning_keywords if kw in query_lower]
    if matched_learning_keywords:
        print(f"[CLASSIFIER] ✓ Learning keywords found: {matched_learning_keywords}")
        print(f"[CLASSIFIER] 📊 Final decision: COMPLEX")
        print(f"{'='*70}\n")
        return "complex"
    
    # Check for greetings
    matched_greetings = [greet for greet in greetings if greet in query_lower]
    if matched_greetings:
        print(f"[CLASSIFIER] ✓ Greeting keywords found: {matched_greetings}")
        print(f"[CLASSIFIER] 📊 Final decision: SIMPLE")
        print(f"{'='*70}\n")
        return "simple"
    
    # Check for short queries
    if len(query_lower.split()) < 5:
        print(f"[CLASSIFIER] ✓ Short query detected (< 5 words)")
        print(f"[CLASSIFIER] 📊 Final decision: SIMPLE")
        print(f"{'='*70}\n")
        return "simple"
    
    # Default to complex for safety
    print(f"[CLASSIFIER] ⚠ No specific patterns matched, defaulting to COMPLEX")
    print(f"[CLASSIFIER] 📊 Final decision: COMPLEX")
    print(f"{'='*70}\n")
    return "complex"


async def generate_classroom_response(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Main function to generate classroom responses.
    Routes to either refiner agent (complex) or direct response (simple).
    """
    # Classify the query
    query_type = classify_query(user_message)
    
    if query_type == "complex":
        print(f"\n{'='*70}")
        print(f"[CLASSIFIER] ✓ Complex query detected")
        print(f"[ORIGINAL QUERY] {user_message}")
        print(f"{'='*70}")
        print(f"[REFINER] Calling refiner agent...")
        
        try:
            refinement_data = await refine_query(user_message)
            
            print(f"\n{'='*70}")
            print(f"[REFINER AGENT RESPONSE]")
            print(f"{'='*70}")
            print(f"Needs Refinement: {refinement_data.get('needs_refinement')}")
            print(f"Reasoning: {refinement_data.get('reasoning')}")
            
            if refinement_data.get('suggestions'):
                print(f"\n� Suggestions Generated:")
                for i, sug in enumerate(refinement_data['suggestions'], 1):
                    print(f"   {i}. Question: {sug['text']}")
                    print(f"      → Adds: {sug['adds']}")
            else:
                print(f"\n✓ No suggestions needed - query is clear")
            
            print(f"{'='*70}\n")
            
            return format_refinement_response(refinement_data)
            
        except Exception as e:
            print(f"\n{'❌'*35}")
            print(f"[REFINER ERROR] {str(e)}")
            print(f"[FALLBACK] Routing to direct Gemini response")
            print(f"{'❌'*35}\n")
            # Fallback: treat as simple query
            return await _direct_gemini_response(user_message, conversation_history)
    else:
        print(f"\n[ROUTING] Simple query detected - Direct response\n")
        return await _direct_gemini_response(user_message, conversation_history)


async def _direct_gemini_response(
    user_message: str, 
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Generate a direct response using Gemini for simple queries.
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
        
        print(f"[CLASSROOM] Processing direct query: {user_message[:80]}...")
        
        # Generate response using Gemini
        response = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-2.0-flash-001',
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000
            )
        )
        
        if response and response.text:
            generated_text = response.text.strip()
            print(f"[CLASSROOM] ✓ Response generated successfully ({len(generated_text)} chars)\n")
            return format_direct_response(generated_text)
        else:
            print("[CLASSROOM] ⚠ Empty response from Gemini API\n")
            return format_direct_response(
                "I apologize, but I couldn't generate a proper response. Could you please rephrase your question?"
            )
            
    except Exception as e:
        print(f"[CLASSROOM] ❌ Error generating response: {str(e)}\n")
        return format_direct_response(
            "I'm experiencing some technical difficulties right now. Please try again in a moment, or rephrase your question."
        )


def format_direct_response(bot_message: str) -> Dict[str, Any]:
    """Format a direct response from the AI."""
    return {
        "response_type": "direct_response",
        "bot_message": bot_message,
        "timestamp": datetime.utcnow(),
        "success": True,
        "source": "gemini-2.0-flash-001"
    }


def format_refinement_response(refinement_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format a refinement response from the refiner agent."""
    return {
        "response_type": "refinement_needed",
        "refinement_data": refinement_data,
        "timestamp": datetime.utcnow(),
        "success": True
    }