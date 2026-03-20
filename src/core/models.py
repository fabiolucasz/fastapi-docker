from sqlalchemy import Column, Integer, String, Boolean
from src.core.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
