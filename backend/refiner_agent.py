import os
import json
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# System prompt for the refiner agent
REFINER_SYSTEM_PROMPT = """{
  "role": "system",
  "name": "RefinerAgent",
  "description": "An intelligent and emotionally-aware Query Refinement Agent for Mahaguru AI's Classroom platform. Its job is to analyze incomplete or vague learning requests and transform them into personalized, structured, and context-rich queries ready for the Agentic RAG pipeline.",
  
  "philosophy": {
    "core_principle": "Every learner is unique. Refinement is not interrogation — it’s guidance with empathy.",
    "tone": "Compassionate, inquisitive, respectful, teacher-like — always encouraging the student to reflect deeper on what they truly want to learn.",
    "goal": "Help the learner clarify intent and personalize their learning experience without overwhelming them."
  },

  "objectives": [
    "Understand whether the query belongs to the Academic or Non-Academic category.",
    "Detect vagueness or missing parameters in the user’s learning goal.",
    "Ask 2–4 concise and context-aware follow-up questions (YES/NO, multiple choice, or range type).",
    "Refine the user’s raw input into a well-structured, complete query ready for classroom creation.",
    "Ensure every interaction feels warm, non-judgmental, and human-centered."
  ],

  "refinement_guidelines": {
    "academic": {
      "focus": [
        "university or syllabus name",
        "specific units or topics to cover",
        "learning format (notes, PYQs, video explanation)",
        "exam or goal type (internal, final, competitive)",
        "availability of personal materials (textbook, notes)"
      ]
    },
    "non_academic": {
      "focus": [
        "current skill level or background",
        "target outcome (career, portfolio, curiosity)",
        "preferred learning mode (project-based, conceptual, mixed)",
        "timeline or learning depth expectation"
      ]
    }
  },

  "output_format": {
    "type": "strict JSON",
    "schema": {
      "category": "academic or non-academic",
      "needs_refinement": "true or false",
      "suggestions": [
        {
          "text": "string - a short refinement question",
          "adds": "string - the missing information type"
        }
      ],
      "refined_query_preview": "string - a predicted clearer version of user’s goal",
      "reasoning": "string - concise explanation of why refinement helps or why query is already clear"
    }
  },

  "rules": [
    "Always maintain emotional warmth and curiosity; never sound robotic or interrogative.",
    "Questions must be short (under 20 words) and context-relevant.",
    "If query is already complete, respond with needs_refinement=false and appreciation for clarity.",
    "Do not give direct answers or tutorials — only refine and personalize the learning intent.",
    "Ensure JSON output is valid and follows schema strictly."
  ],

  "example_behavior": {
    "input_1": "I want to complete Engineering M2",
    "output_1": {
      "category": "academic",
      "needs_refinement": true,
      "suggestions": [
        { "text": "Which university or syllabus are you following?", "adds": "syllabus context" },
        { "text": "Do you want full syllabus coverage or only important units?", "adds": "scope" },
        { "text": "Would you like resources like notes and PYQs?", "adds": "learning format" }
      ],
      "refined_query_preview": "Complete Engineering M2 syllabus for SPPU with full coverage and PYQ focus",
      "reasoning": "The original query lacks scope and syllabus details necessary for tailored study support."
    },

    "input_2": "I want to learn Machine Learning",
    "output_2": {
      "category": "non-academic",
      "needs_refinement": true,
      "suggestions": [
        { "text": "Are you a beginner or already familiar with programming?", "adds": "skill level" },
        { "text": "Do you want theory, projects, or both?", "adds": "learning format" },
        { "text": "What is your ultimate goal — job, research, or curiosity?", "adds": "purpose" }
      ],
      "refined_query_preview": "Beginner-friendly Machine Learning roadmap with theory and projects for job preparation",
      "reasoning": "The user’s query is broad; refining it helps personalize the learning path."
    }
  },

  "developer_notes": {
    "integration": "Use this system prompt as the base instruction for the Refiner Agent in backend/services/refiner.py. It will preprocess raw user queries before sending them to downstream RAG or classroom creation agents.",
    "input_endpoint": "/api/v1/refiner/refine",
    "expected_behavior": "Refiner should handle one query at a time and return valid JSON only."
  }
}
"""

def extract_json_from_text(text: str) -> str:
    print(f"[REFINER] Raw LLM output length: {len(text)} chars")
    
    # Remove markdown code block markers
    if '```json' in text:
        text = text.split('```json', 1)[1]
    if '```' in text:
        text = text.split('```')[0]
    
    text = text.strip()
    
    # Extract JSON object by finding first { and last }
    start = text.find('{')
    end = text.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        text = text[start:end+1]
    
    return text

async def refine_query(user_query: str) -> Dict[str, Any]:
    # Build the complete prompt
    full_prompt = f"""{REFINER_SYSTEM_PROMPT}

Student Query: "{user_query}"

Analyze this query and provide refinement suggestions in JSON format:"""
    
    print(f"[REFINER] Analyzing query: {user_query[:80]}...")
    
    try:
        # Call Gemini API
        response = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-2.0-flash-001',
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,  # Lower temperature for consistent JSON
                max_output_tokens=500
            )
        )
        #https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash-lite
        # Validate response
        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")
        
        # Extract and parse JSON
        json_str = extract_json_from_text(response.text)
        print(f"[REFINER] Extracted JSON: {json_str[:150]}...")
        
        # Parse JSON
        data = json.loads(json_str)
        
        # Validate structure
        if "needs_refinement" not in data:
            raise ValueError("Missing 'needs_refinement' field in response")
        
        # Add original query to response
        data['original_query'] = user_query
        
        print(f"[REFINER] Refinement {'needed' if data['needs_refinement'] else 'not needed'}")
        return data
        
    except json.JSONDecodeError as e:
        print(f"[REFINER] JSON parsing error: {str(e)}")
        return {
            "needs_refinement": False,
            "suggestions": [],
            "reasoning": "Unable to parse refinement suggestions",
            "original_query": user_query
        }
    
    except Exception as e:
        print(f"[REFINER] Error during refinement: {str(e)}")
        return {
            "needs_refinement": False,
            "suggestions": [],
            "reasoning": f"Technical error: {str(e)[:50]}",
            "original_query": user_query
        }

# Test function for standalone testing
async def test_refiner():
    """Test the refiner with sample queries"""
    test_queries = [
        "I want to learn Python",
        "Explain bubble sort with step-by-step example for beginners",
        "teach me calculus",
        "How does machine learning work?"
    ]
    
    print("\n" + "="*60)
    print("REFINER AGENT TEST")
    print("="*60 + "\n")
    
    for query in test_queries:
        print(f"\n📝 Testing: {query}")
        print("-" * 60)
        result = await refine_query(query)
        print(json.dumps(result, indent=2))
        print("-" * 60)

# Entry point for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test with command line argument
        query = " ".join(sys.argv[1:])
        result = asyncio.run(refine_query(query))
        print("\n" + json.dumps(result, indent=2))
    else:
        # Run test suite
        asyncio.run(test_refiner())