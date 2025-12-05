from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas.schemas import User
from ..models import models
from ..database import get_db
from ..auth import auth

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/me/", response_model=User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # For now, allow any logged-in user to view any user's public profile (username, email, created_at)
    # More restrictive access can be implemented later if needed.
    return user