import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "your-huggingface-api-key-here")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")

ACADEMIC_KEYWORDS = [
    "exam", "study", "homework", "assignment", "course", "syllabus", "subject", "topic", "school", "university", "college", "test", "grade", "board", "curriculum"
]
SUBJECT_KEYWORDS = {
    "math": "Mathematics",
    "science": "Science",
    "history": "History",
    "physics": "Physics",
    "chemistry": "Chemistry",
    "biology": "Biology",
    "english": "English",
    "geography": "Geography",
    "computer": "Computer Science",
    "economics": "Economics"
}

class LLMClient:
    """
    Abstracts LLM calls for classification and refinement.
    Supports HuggingFace and Gemini APIs. Extendable for future LLMs.
    """
    def __init__(self, provider: str = "huggingface"):
        self.provider = provider
        self.api_key = HUGGINGFACE_API_KEY if provider == "huggingface" else GEMINI_API_KEY

    def grammar_improve(self, query: str) -> str:
        # Placeholder for LLM grammar improvement
        return query.strip().capitalize()

class RefinerAgent:
    def __init__(self, llm_provider: str = "huggingface"):
        self.llm = LLMClient(provider=llm_provider)

    def classify_query(self, query: str) -> str:
        if any(word in query.lower() for word in ACADEMIC_KEYWORDS):
            return "academic"
        return "general"

    def refine_query(self, query: str, query_type: str) -> Dict:
        response = {
            "original_query": query,
            "refined_query": self.llm.grammar_improve(query),
            "query_type": query_type,
            "subject": None,
            "syllabus": None,
            "exam_focus": None,
            "missing_info": [],
            "suggestions": []
        }
        if query_type == "academic":
            subject = None
            for key, val in SUBJECT_KEYWORDS.items():
                if key in query.lower():
                    subject = val
                    break
            response["subject"] = subject
            # Syllabus detection
            if "cbse" in query.lower():
                response["syllabus"] = "CBSE"
            elif "icse" in query.lower():
                response["syllabus"] = "ICSE"
            # Exam focus
            if "exam" in query.lower():
                response["exam_focus"] = "Exam Preparation"
            # Missing info detection
            if not subject:
                response["missing_info"].append("Subject not specified")
            if not response["syllabus"]:
                response["missing_info"].append("Syllabus not specified")
            if not response["exam_focus"]:
                response["missing_info"].append("Exam focus not specified")
            if not any(word in query.lower() for word in ["topic", "chapter", "lesson"]):
                response["missing_info"].append("Topic not specified")
            # Suggestions
            if not subject:
                response["suggestions"].append("Add subject area")
            if not response["syllabus"]:
                response["suggestions"].append("Specify syllabus or board")
            if not response["exam_focus"]:
                response["suggestions"].append("Mention exam focus if relevant")
            response["suggestions"].append("Include educational level (grade/class)")
            response["suggestions"].append("Specify topic or chapter")
        else:
            # General queries: grammar/clarity only
            response["refined_query"] = self.llm.grammar_improve(query)
        return response

    async def log_refined_query(self, db, original_query, refined_query, query_type, missing_info, user_id):
        # Implement the logic to log the refined query to the database
        # This is a placeholder implementation; replace it with actual logic
        db_obj = await db.execute(
            """
            INSERT INTO refined_queries (original_query, refined_query, query_type, missing_info, user_id)
            VALUES (:original_query, :refined_query, :query_type, :missing_info, :user_id)
            RETURNING id, original_query, refined_query, query_type, missing_info, timestamp, user_id
            """,
            {
                "original_query": original_query,
                "refined_query": refined_query,
                "query_type": query_type,
                "missing_info": missing_info,
                "user_id": user_id,
            }
        )
        return db_obj.fetchone()
