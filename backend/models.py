from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

# Chat request model for both StudentGPT and Classroom
class ChatRequest(BaseModel):
    message: str

# Chat response model
class ChatResponse(BaseModel):
    response: str

# Classroom-specific models
class ClassroomChatRequest(BaseModel):
    user_message: str
    user_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

class ClassroomChatResponse(BaseModel):
    bot_message: str
    timestamp: datetime
    success: bool

# Auth models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
