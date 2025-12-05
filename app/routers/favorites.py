from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..schemas.schemas import UserFavorite
from ..models import models
from ..database import get_db
from ..auth import auth

router = APIRouter(
    prefix="/users",
    tags=["users", "favorites"]
)

@router.get("/{user_id}/favorites", response_model=List[UserFavorite])
def read_user_favorites(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this user's favorites")

    favorites = db.query(models.UserFavorite).filter(models.UserFavorite.user_id == user_id)\
        .options(joinedload(models.UserFavorite.anime))\
        .options(joinedload(models.UserFavorite.character))\
        .all()
    
    return favorites
