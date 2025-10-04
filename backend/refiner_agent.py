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
REFINER_SYSTEM_PROMPT = """You are a Query Refinement Assistant for an educational platform.

Your job: Analyze student queries and suggest improvements to make them clearer and more specific.

Rules:
1. Only suggest refinements if the query is vague, too broad, or missing context
2. Generate 2-3 SHORT suggestions (each under 15 words)
3. Each suggestion should be a YES/NO question or a specific addition
4. Focus on: skill level, learning goal, format preference, scope, or prerequisites
5. Keep suggestions practical and educational

Output Format (strict JSON):
{
  "needs_refinement": true or false,
  "suggestions": [
    {
      "text": "Are you a beginner or do you have prior experience?",
      "adds": "skill level"
    }
  ],
  "reasoning": "brief explanation why refinement helps or why query is clear"
}

If the query is already clear and specific, return:
{
  "needs_refinement": false,
  "suggestions": [],
  "reasoning": "Query is clear and specific"
}"""

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