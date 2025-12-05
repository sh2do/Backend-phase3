from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas.schemas import Genre, GenreBase
from ..models import models
from ..database import get_db
from ..auth import auth

router = APIRouter(
    prefix="/genres",
    tags=["genres"]
)

@router.post("/", response_model=Genre, status_code=status.HTTP_201_CREATED)
def create_genre(
    genre: GenreBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_genre = db.query(models.Genre).filter(models.Genre.name == genre.name).first()
    if db_genre:
        raise HTTPException(status_code=400, detail="Genre name already registered")
    
    db_genre = models.Genre(**genre.dict())
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre

@router.get("/", response_model=List[Genre])
def read_genres(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    genres = db.query(models.Genre).offset(skip).limit(limit).all()
    return genres

@router.get("/{genre_id}", response_model=Genre)
def read_genre(
    genre_id: int,
    db: Session = Depends(get_db)
):
    genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if genre is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre

@router.put("/{genre_id}", response_model=Genre)
def update_genre(
    genre_id: int,
    genre: GenreBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if db_genre is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    
    for key, value in genre.dict(exclude_unset=True).items():
        setattr(db_genre, key, value)
    
    db.commit()
    db.refresh(db_genre)
    return db_genre

@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_genre(
    genre_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if db_genre is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    
    db.delete(db_genre)
    db.commit()
    return {"ok": True}