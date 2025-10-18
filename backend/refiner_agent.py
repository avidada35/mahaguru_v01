import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from models import ConversationTurn, FinalRefinementPackage

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
        
        # Add question_id to each suggestion
        if "suggestions" in data and isinstance(data["suggestions"], list):
            for i, suggestion in enumerate(data["suggestions"]):
                suggestion["question_id"] = f"q_{i+1}"
        
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

async def continue_refinement(original_query: str, user_answers: List[Dict]) -> Dict[str, Any]:
    """
    Continue multi-turn refinement based on user answers.
    
    Args:
        original_query: The original user query
        user_answers: List of user answers with question_id and answer
    
    Returns:
        Dict with either follow-up questions or finalized refinement
    """
    print(f"[REFINER] Continuing refinement for: {original_query[:80]}...")
    
    # Format user answers for the prompt
    answers_context = "\n".join([
        f"Q{answer['question_id']}: {answer['answer']}" 
        for answer in user_answers
    ])
    
    # Build prompt for continuation
    continue_prompt = f"""
Based on the original query and user's answers, determine if more refinement is needed or if we can finalize.

Original Query: "{original_query}"

User's Answers:
{answers_context}

Guidelines:
- Maximum 2 rounds of refinement total
- If enough context is gathered, set needs_refinement=false
- If more clarification needed, ask 1-2 focused follow-up questions
- Questions should build on previous answers

Respond in JSON format with the same structure as before.
"""
    
    try:
        # Call Gemini API
        response = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-2.0-flash-001',
            contents=continue_prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=500
            )
        )
        
        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")
        
        # Extract and parse JSON
        json_str = extract_json_from_text(response.text)
        print(f"[REFINER] Continue refinement JSON: {json_str[:150]}...")
        
        data = json.loads(json_str)
        
        # Validate structure
        if "needs_refinement" not in data:
            raise ValueError("Missing 'needs_refinement' field in response")
        
        # Add question_id to each new suggestion
        if "suggestions" in data and isinstance(data["suggestions"], list):
            for i, suggestion in enumerate(data["suggestions"]):
                suggestion["question_id"] = f"q_followup_{i+1}"
        
        # Ensure consistent data structure
        needs_refinement = data.get('needs_refinement', True)
        
        if needs_refinement:
            # More refinement needed
            return {
                "needs_refinement": True,
                "suggestions": data.get('suggestions', []),
                "reasoning": data.get('reasoning', ''),
                "original_query": original_query,
                "final_package": None
            }
        else:
            # Refinement complete - generate final package
            print("[REFINER] Refinement complete, generating final package...")
            
            # Build conversation history from user answers
            conversation_history = []
            for answer_data in user_answers:
                conversation_history.append({
                    "question_id": answer_data.get("question_id", ""),
                    "question": f"Question {answer_data.get('question_id', '')}",  # We don't store original questions, so use placeholder
                    "answer": answer_data.get("answer", "")
                })
            
            # Generate final package
            final_package = await finalize_refinement_package(
                original_query=original_query,
                conversation_history=conversation_history,
                all_reasoning=data.get('reasoning', ''),
                rounds=len(user_answers)  # Use number of answers as approximation of rounds
            )
            
            return {
                "needs_refinement": False,
                "suggestions": [],  # Empty when complete
                "reasoning": "",     # Empty when complete
                "original_query": original_query,
                "final_package": final_package
            }
        
        print(f"[REFINER] Continue refinement {'needed' if needs_refinement else 'complete'}")
        
    except json.JSONDecodeError as e:
        print(f"[REFINER] JSON parsing error in continue_refinement: {str(e)}")
        
        # Create fallback response and generate final package since we're ending refinement
        fallback_data = {
            "needs_refinement": False,
            "suggestions": [],
            "reasoning": "Refinement completed based on provided answers",
            "original_query": original_query
        }
        
        # Generate final package for fallback
        conversation_history = []
        for answer_data in user_answers:
            conversation_history.append({
                "question_id": answer_data.get("question_id", ""),
                "question": f"Question {answer_data.get('question_id', '')}",
                "answer": answer_data.get("answer", "")
            })
        
        final_package = await finalize_refinement_package(
            original_query=original_query,
            conversation_history=conversation_history,
            all_reasoning="Refinement completed based on provided answers",
            rounds=len(user_answers)
        )
        
        fallback_data['final_package'] = final_package
        return fallback_data
    
    except Exception as e:
        print(f"[REFINER] Error during continue_refinement: {str(e)}")
        
        # Create fallback response and generate final package since we're ending refinement
        fallback_data = {
            "needs_refinement": False,
            "suggestions": [],
            "reasoning": f"Technical error: {str(e)[:50]}",
            "original_query": original_query
        }
        
        # Generate final package for fallback
        conversation_history = []
        for answer_data in user_answers:
            conversation_history.append({
                "question_id": answer_data.get("question_id", ""),
                "question": f"Question {answer_data.get('question_id', '')}",
                "answer": answer_data.get("answer", "")
            })
        
        final_package = await finalize_refinement_package(
            original_query=original_query,
            conversation_history=conversation_history,
            all_reasoning=f"Technical error: {str(e)[:50]}",
            rounds=len(user_answers)
        )
        
        fallback_data['final_package'] = final_package
        return fallback_data

async def finalize_refinement_package(
    original_query: str,
    conversation_history: List[Dict],
    all_reasoning: str,
    rounds: int
) -> Dict[str, Any]:
    """
    Generate final refinement package combining original query with Q&A answers.
    
    Args:
        original_query: The user's original query
        conversation_history: List of question-answer pairs
        all_reasoning: Combined reasoning from all refinement rounds
        rounds: Number of refinement rounds completed
    
    Returns:
        Dict containing FinalRefinementPackage structure
    """
    print(f"[REFINER] Finalizing refinement package for: {original_query[:80]}...")
    
    # Build conversation context for Gemini
    conversation_context = ""
    for i, qa in enumerate(conversation_history, 1):
        conversation_context += f"Q{i}: {qa.get('question', '')}\nA{i}: {qa.get('answer', '')}\n\n"
    
    # Prompt for generating refined query and extracting requirements
    finalization_prompt = f"""
Based on the original query and the conversation history, create a comprehensive learning request package.

Original Query: "{original_query}"

Conversation History:
{conversation_context}

Previous Reasoning: {all_reasoning}

Generate a JSON response with:
1. refined_query: An enhanced, clear version of the original query that incorporates all gathered context
2. requirements: List of specific requirements/constraints extracted from the answers (e.g., "beginner level", "project-based", "exam preparation")
3. tags: Categorization tags including academic/non-academic and subject areas
4. confidence: Score from 0.7 to 1.0 based on completeness of information gathered

Format as JSON:
{{
  "refined_query": "Enhanced query text here",
  "requirements": ["requirement1", "requirement2", ...],
  "tags": ["tag1", "tag2", ...],
  "confidence": 0.85
}}
"""
    
    try:
        # Call Gemini for refinement finalization
        response = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-2.0-flash-001',
            contents=finalization_prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=800
            )
        )
        
        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")
        
        # Extract and parse JSON
        json_str = extract_json_from_text(response.text)
        gemini_data = json.loads(json_str)
        
        # Convert conversation history to ConversationTurn format
        conversation_turns = []
        for qa in conversation_history:
            conversation_turns.append({
                "question_id": qa.get("question_id", ""),
                "question": qa.get("question", ""),
                "answer": qa.get("answer", "")
            })
        
        # Build final package
        final_package = {
            "original_query": original_query,
            "refined_query": gemini_data.get("refined_query", original_query),
            "conversation_history": conversation_turns,
            "requirements": gemini_data.get("requirements", []),
            "reasoning": all_reasoning,
            "refinement_rounds": rounds,
            "confidence": gemini_data.get("confidence", 0.8),
            "tags": gemini_data.get("tags", []),
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"[REFINER] Package created with confidence: {final_package['confidence']}")
        return final_package
        
    except json.JSONDecodeError as e:
        print(f"[REFINER] JSON parsing error in finalization: {str(e)}")
        # Fallback package
        return {
            "original_query": original_query,
            "refined_query": original_query,
            "conversation_history": [{"question_id": qa.get("question_id", ""), "question": qa.get("question", ""), "answer": qa.get("answer", "")} for qa in conversation_history],
            "requirements": [],
            "reasoning": all_reasoning,
            "refinement_rounds": rounds,
            "confidence": 0.7,
            "tags": ["general"],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"[REFINER] Error during finalization: {str(e)}")
        # Fallback package
        return {
            "original_query": original_query,
            "refined_query": original_query,
            "conversation_history": [{"question_id": qa.get("question_id", ""), "question": qa.get("question", ""), "answer": qa.get("answer", "")} for qa in conversation_history],
            "requirements": [],
            "reasoning": all_reasoning,
            "refinement_rounds": rounds,
            "confidence": 0.7,
            "tags": ["general"],
            "timestamp": datetime.now().isoformat()
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