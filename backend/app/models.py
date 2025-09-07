from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Detailed user information
    unit = Column(String, nullable=False)
    global_role = Column(String, nullable=True) # e.g., 'super_admin', 'regional_admin'
    roles_by_project = Column(JSON, nullable=True) # e.g., {"heating_plan_2025-2026": "filler"}
