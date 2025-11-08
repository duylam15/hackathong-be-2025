from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db

# Dependency to get database session
def get_database() -> Generator:
    """Get database session"""
    try:
        db = next(get_db())
        yield db
    finally:
        pass
