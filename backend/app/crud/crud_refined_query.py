from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refined_query import RefinedQuery
from app.schemas.refined_query import RefinedQueryCreate

class CRUDRefinedQuery:
    async def create(self, db: AsyncSession, obj_in: RefinedQueryCreate) -> RefinedQuery:
        db_obj = RefinedQuery(
            original_query=obj_in.original_query,
            refined_query=obj_in.refined_query,
            query_type=obj_in.query_type,
            missing_info=obj_in.missing_info,
            user_id=obj_in.user_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

crud_refined_query = CRUDRefinedQuery()
