from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db

# Re-export get_db for clean dependency injection in routers
DbSession = Depends(get_db)
