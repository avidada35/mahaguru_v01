from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import (
    ChatRequest, ChatResponse, RegisterRequest, 
    TokenResponse, UserResponse, ClassroomChatRequest, ClassroomChatResponse
)
from classroom import generate_classroom_response, format_response_with_metadata

app = FastAPI(title="Mahaguru AI Backend", version="1.0.0")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Frontend development server
        "http://localhost:5173",    # Vite default port
        "http://127.0.0.1:3000",    # Alternative localhost
        "http://127.0.0.1:5173"     # Alternative localhost for Vite
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Mahaguru AI Backend"}

# For Brainstorming (StudentGPT)
@app.post("/api/v1/studentgpt/chat", response_model=ChatResponse)
async def studentgpt_chat(request: ChatRequest):
    # Your fine-tuned small LLM logic here
    # For now, returning a simple mock response
    response = f"StudentGPT: I understand you asked about '{request.message}'. This is a placeholder response. Implement your fine-tuned small LLM logic here."
    return ChatResponse(response=response)

# For Classroom (Multi-agent)
@app.post("/api/v1/classroom/chat", response_model=ClassroomChatResponse)
async def classroom_chat(request: ClassroomChatRequest):
    """
    Classroom chat endpoint using Gemini API for educational conversations
    """
    try:
        print(f"[API] Received classroom chat request from user: {request.user_id}")
        print(f"[API] User message: '{request.user_message}'")
        
        # Generate response using Gemini API
        bot_message = await generate_classroom_response(
            user_message=request.user_message,
            conversation_history=request.conversation_history
        )
        
        print(f"[API] Bot response (first 100 chars): '{bot_message[:100]}...'")
        print(f"[API] Sending response to frontend")
        
        # Format response with metadata
        response_data = format_response_with_metadata(bot_message)
        
        return ClassroomChatResponse(**response_data)
        
    except Exception as e:
        print(f"[API] Error in classroom chat: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while processing your request. Please try again."
        )

# Basic auth endpoints that frontend expects
@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    # Simple mock login - implement proper authentication logic
    if username and password:
        return TokenResponse(access_token="mock_token_123", token_type="bearer")
    raise HTTPException(status_code=400, detail="Invalid credentials")

@app.post("/api/v1/auth/register")
async def register(request: RegisterRequest):
    # Simple mock registration - implement proper registration logic
    return {"message": "User registered successfully", "email": request.email}

@app.get("/api/v1/users/me", response_model=UserResponse)
async def get_current_user():
    # Mock current user - implement proper user authentication
    return UserResponse(id=1, email="user@example.com", full_name="Mock User")

@app.post("/api/v1/auth/logout")
async def logout():
    return {"message": "Logged out successfully"}

@app.post("/api/v1/auth/refresh")
async def refresh_token():
    # Mock token refresh
    return TokenResponse(access_token="new_mock_token_456", token_type="bearer")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
