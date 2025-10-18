from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

# ==================== CHAT MODELS ====================

class ChatRequest(BaseModel):
    """Generic chat request model"""
    message: str

class ChatResponse(BaseModel):
    """Generic chat response model"""
    response: str

# ==================== REFINEMENT MODELS ====================

class RefinementSuggestion(BaseModel):
    """
    A single suggestion for refining a user query.
    
    Attributes:
        question_id: Unique identifier for this question/suggestion
        text: The suggestion question or addition (e.g., 'Are you a beginner?')
        adds: What context this suggestion would add (e.g., 'skill level')
    """
    question_id: str
    text: str
    adds: str

class RefinementData(BaseModel):
    """
    Structured data for query refinement from the refiner agent.
    
    Attributes:
        needs_refinement: Whether the query needs refinement
        suggestions: List of suggestions/questions to improve the query
        reasoning: Brief explanation for why refinement is/isn't needed
        original_query: The original user query before refinement
    """
    needs_refinement: bool
    suggestions: List[RefinementSuggestion]
    reasoning: str
    original_query: str

class UserAnswer(BaseModel):
    """
    User's answer to a refinement question.
    
    Attributes:
        question_id: The ID of the question being answered
        answer: The user's answer/response
    """
    question_id: str
    answer: str

class ContinueRefinementRequest(BaseModel):
    """
    Request model for continuing multi-turn refinement.
    
    Attributes:
        original_query: The original user query
        answers: List of user answers to previous questions
    """
    original_query: str
    answers: List[UserAnswer]

class ConversationTurn(BaseModel):
    """
    A single turn in the refinement conversation.
    
    Attributes:
        question_id: Unique identifier for the question
        question: The question text that was asked
        answer: The user's answer to the question
    """
    question_id: str
    question: str
    answer: str

class FinalRefinementPackage(BaseModel):
    """
    Final structured package combining user's original query with Q&A answers.
    
    Attributes:
        original_query: The user's original query
        refined_query: Enhanced version of the original query
        conversation_history: List of question-answer turns
        requirements: Extracted requirements and constraints
        reasoning: Combined reasoning from all refinement rounds
        refinement_rounds: Number of refinement rounds completed
        confidence: Confidence score (0.0-1.0) in the refinement quality
        tags: Categorization tags (academic/non-academic, subject areas)
        timestamp: ISO 8601 timestamp when package was created
    """
    original_query: str
    refined_query: str
    conversation_history: List[ConversationTurn]
    requirements: List[str]
    reasoning: str
    refinement_rounds: int
    confidence: float
    tags: List[str]
    timestamp: str

class ContinueRefinementResponse(BaseModel):
    """
    Response model for continuing refinement - same structure as RefinementData.
    """
    needs_refinement: bool
    suggestions: List[RefinementSuggestion] = []  # Make optional with default
    reasoning: str = ""  # Make optional with default
    original_query: str
    final_package: Optional[FinalRefinementPackage] = None

# ==================== CLASSROOM MODELS ====================

class ClassroomChatRequest(BaseModel):
    """
    Request model for classroom chat endpoint.
    
    Attributes:
        user_message: The student's question or message
        user_id: Optional user identifier
        conversation_history: Optional list of previous messages for context
    """
    user_message: str
    user_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

class ClassroomChatResponse(BaseModel):
    response_type: str  # 'direct_response' or 'refinement_needed'
    bot_message: Optional[str] = None  # Only for direct responses
    source: Optional[str] = None       # Only for direct responses
    refinement_data: Optional[RefinementData] = None  # Only for refinement responses
    timestamp: datetime
    success: bool

# ==================== AUTH MODELS ====================

class LoginRequest(BaseModel):
    """User login request"""
    username: str
    password: str

class RegisterRequest(BaseModel):
    """User registration request"""
    email: str
    password: str
    full_name: Optional[str] = None

class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    """User information response"""
    id: int
    email: str
    full_name: Optional[str] = None