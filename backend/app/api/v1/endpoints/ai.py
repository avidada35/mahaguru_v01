from typing import Any, Dict, List, Optional
import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_current_active_user
from app.services.retrieval_service import HybridRetriever
from app.services.embedding_service import get_embedding_service
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ai"])
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_RESULTS = 50
RERANK_TOP_K = 10

class SearchResult(BaseModel):
    """Schema for a single search result."""
    chunk_id: int
    document_id: int
    score: float
    text: str
    metadata: Dict[str, Any]

# Router without prefix; v1 aggregator applies "/ai" prefix
router = APIRouter(tags=["ai"])

# Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_RESULTS = 50
RERANK_TOP_K = 10

class SearchRequest(BaseModel):
    """Schema for document search request."""
    query: str = Field(..., description="The search query")
    document_ids: Optional[List[int]] = Field(
        None,
        description="Filter by specific document IDs"
    )
    top_k: int = Field(
        MAX_RESULTS,
        gt=0,
        le=100,
        description="Maximum number of results to return"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional filters for the search"
    )
    use_hybrid: bool = Field(
        True,
        description="Whether to use hybrid search (dense + sparse)"
    )
    use_reranker: bool = Field(
        True,
        description="Whether to use reranking for better results"
    )

class SearchResponse(BaseModel):
    """Schema for search response."""
    results: List[SearchResult]
    total: int
    model: str
    query: str

class AnswerRequest(SearchRequest):
    """Schema for answer generation request."""
    max_tokens: int = Field(
        1000,
        gt=0,
        le=4000,
        description="Maximum number of tokens in the generated answer"
    )
    temperature: float = Field(
        0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for answer generation"
    )

class AnswerResponse(BaseModel):
    """Schema for answer generation response."""
    answer: str
    sources: List[SearchResult]
    model: str
    tokens_used: int


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """
    Search through documents using hybrid retrieval (dense + sparse).
    
    This endpoint performs a semantic search across the user's documents,
    returning the most relevant chunks based on the query.
    """
    embedding_service = await get_embedding_service()
    
    # Initialize retriever
    retriever = HybridRetriever()
    
    # Perform search
    results = await retriever.retrieve_documents(
        query=request.query,
        top_k=request.top_k
    )
    
    # Convert to response model
    search_results = [
        SearchResult(
            chunk_id=result.get("id", 0),
            document_id=result.get("id", 0),  # Assuming same for now
            score=result.get("score", 0.0),
            text=result.get("content", ""),
            metadata=result.get("metadata", {})
        )
        for result in results
    ]
    
    return SearchResponse(
        results=search_results,
        total=len(search_results),
        model="default",  # Placeholder
        query=request.query
    )

@router.post("/answer", response_model=AnswerResponse)
async def generate_answer(
    request: AnswerRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> AnswerResponse:
    """
    Generate an answer to a question based on the user's documents.
    
    This endpoint first retrieves relevant document chunks and then uses
    them as context to generate a natural language answer.
    """
    # Get embedding service
    embedding_service = await get_embedding_service()
    
    # Initialize retriever
    retriever = HybridRetriever()
    
    # Perform search to get relevant chunks
    results = await retriever.retrieve_documents(
        query=request.query,
        top_k=request.top_k
    )
    
    # Format context from top results
    context = "\n\n".join(
        f"[Document {i+1}, Score: {result.get('score', 0):.2f}]\n{result.get('content', '')}"
        for i, result in enumerate(results[:RERANK_TOP_K])
    )
    
    # Generate answer using the context
    # In a real implementation, this would call an LLM
    answer = await _generate_answer_with_llm(
        query=request.query,
        context=context,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )
    
    # Convert results to response model
    source_results = [
        SearchResult(
            chunk_id=result.get("id", 0),
            document_id=result.get("id", 0),  # Assuming same for now
            score=result.get("score", 0.0),
            text=result.get("content", ""),
            metadata=result.get("metadata", {})
        )
        for result in results[:RERANK_TOP_K]
    ]
    
    return AnswerResponse(
        answer=answer,
        sources=source_results,
        model="default",  # Placeholder
        tokens_used=len(answer.split())  # Approximate
    )

async def _generate_answer_with_llm(
    query: str,
    context: str,
    max_tokens: int = 1000,
    temperature: float = 0.7
) -> str:
    """
    Generate an answer using an LLM with the given context.
    
    This is a placeholder implementation that simulates an LLM call.
    In a real implementation, this would call an actual LLM API.
    """
    # This is a simplified example - in a real implementation, you would:
    # 1. Call an LLM API (e.g., OpenAI, Anthropic, etc.)
    # 2. Format the prompt with the query and context
    # 3. Parse and return the response
    
    prompt = f"""You are an AI assistant that answers questions based on the provided context.
    
    Context:
    {context}
    
    Question: {query}
    
    Answer the question based on the context above. If the context doesn't contain
    enough information to answer the question, say "I don't have enough information
    to answer this question based on the provided documents."
    """
    
    # Simulate LLM call
    # In a real implementation, you would make an API call here
    await asyncio.sleep(0.1)  # Simulate network delay
    
    # Return a simple response for demonstration
    return (
        "Based on the provided documents, here's the answer to your question:\n\n"
        f"{query}\n\n"
        "This is a placeholder response. In a real implementation, this would be "
        "generated by an LLM based on the retrieved document chunks."
    )


async def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding vector for the given text using the embedding service.
    
    Args:
        text: The text to embed
        
    Returns:
        A list of floats representing the embedding vector
    """
    embedding_service = await get_embedding_service()
    result = await embedding_service.embed_texts([text])
    return result.embeddings[0] if result.embeddings else []


@router.post("/documents/{document_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_document(
    *,
    document_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate processing of a document (extract text, generate embeddings, etc.).
    
    This endpoint starts an asynchronous task to process the document.
    """
    # Check if document exists and user has access
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    # Use .owner_id and .is_superuser as attributes, not SQLAlchemy columns
    if getattr(document, "owner_id", None) != getattr(current_user, "id", None) and not getattr(current_user, "is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    user_id = getattr(current_user, "id", None)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User ID is required.")
    background_tasks.add_task(
        _process_document_task,
        document_id=document_id,
        user_id=int(user_id)
    )
    return {
        "status": "processing_started",
        "document_id": document_id,
        "message": "Document processing has been queued"
    }

async def _process_document_task(document_id: int, user_id: int):
    """Background task to process a document."""
    from app.utils.document_processor import DocumentProcessor
    from app.db.session import AsyncSessionLocal
    from app.models.document import Document
    from sqlalchemy import select
    db = AsyncSessionLocal()
    try:
        result = db.execute(select(Document).where(Document.id == document_id))
        document = result.scalars().one_or_none()
        if not document:
            logger.error(f"Document {document_id} not found")
            return
        processor = DocumentProcessor()
        success, message = await processor.process_document(document, db)
        if success:
            logger.info(f"Successfully processed document {document_id}: {message}")
        else:
            logger.error(f"Failed to process document {document_id}: {message}")
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)
    finally:
        db.close()
