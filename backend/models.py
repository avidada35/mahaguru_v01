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
        text: The suggestion question or addition (e.g., 'Are you a beginner?')
        adds: What context this suggestion would add (e.g., 'skill level')
    """
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
    """
    Response from the classroom chat endpoint.
    Supports both direct responses and refinement responses.
    
    Attributes:
        response_type: Either 'direct_response' or 'refinement_needed'
        bot_message: The AI's direct response (only for direct_response type)
        source: The model used to generate response (only for direct_response type)
        refinement_data: Structured refinement suggestions (only for refinement_needed type)
        timestamp: When the response was generated
        success: Whether the request was successful
    """
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