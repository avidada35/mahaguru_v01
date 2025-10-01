from typing import List, Optional
from pydantic import BaseModel, Field

class RefinedQueryRequest(BaseModel):
    original_query: str = Field(..., min_length=1, description="User's raw query")

class RefinedQueryResponse(BaseModel):
    original_query: str
    refined_query: str
    query_type: str  # "academic" or "general"
    subject: Optional[str] = None
    syllabus: Optional[str] = None
    exam_focus: Optional[str] = None
    missing_info: List[str] = []
    suggestions: List[str] = []
