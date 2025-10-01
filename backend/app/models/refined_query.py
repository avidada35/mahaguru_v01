from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class RefinedQuery(Base):
    __tablename__ = "refined_queries"

    id = Column(Integer, primary_key=True, index=True)
    original_query = Column(Text, nullable=False)
    refined_query = Column(JSONB, nullable=False)
    query_type = Column(String, nullable=False)
    missing_info = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)

    user = relationship("User", back_populates="refined_queries")
