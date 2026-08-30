"""
Base model with common fields for all database models
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from app.core.database import Base


def get_utc_now():
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)


class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)