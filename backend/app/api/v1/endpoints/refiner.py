from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.services.refiner import RefinerAgent
from app.schemas.refined_query import RefinedQueryRequest, RefinedQueryResponse

router = APIRouter()
refiner_agent = RefinerAgent()

@router.post("/refiner/refine", response_model=RefinedQueryResponse)
async def refine_query_endpoint(
    request: RefinedQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not request.original_query or not request.original_query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="original_query is required.")
    try:
        query_type = refiner_agent.classify_query(request.original_query)
        refined = refiner_agent.refine_query(request.original_query, query_type)
        # Ensure missing_info is always a list
        missing_info = refined.get("missing_info", [])
        if query_type == "academic":
            if not refined.get("subject"):
                missing_info.append("Subject not specified")
            if not refined.get("topic"):
                missing_info.append("Topic not specified")
        db_obj = await refiner_agent.log_refined_query(
            db,
            original_query=request.original_query,
            refined_query=refined.get("refined_query", request.original_query),
            query_type=query_type,
            missing_info=missing_info,
            user_id=getattr(current_user, "id", None)
        )
        return RefinedQueryResponse(
            original_query=getattr(db_obj, "original_query", request.original_query),
            refined_query=getattr(db_obj, "refined_query", refined.get("refined_query", request.original_query)),
            query_type=getattr(db_obj, "query_type", query_type),
            subject=getattr(db_obj, "subject", refined.get("subject", None)),
            syllabus=getattr(db_obj, "syllabus", refined.get("syllabus", None)),
            exam_focus=getattr(db_obj, "exam_focus", refined.get("exam_focus", None)),
            missing_info=getattr(db_obj, "missing_info", missing_info),
            suggestions=getattr(db_obj, "suggestions", refined.get("suggestions", []))
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Refinement error: {str(e)}")
