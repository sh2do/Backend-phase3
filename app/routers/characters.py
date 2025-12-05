from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..schemas.schemas import Character, CharacterBase
from ..models import models
from ..database import get_db
from ..auth import auth

router = APIRouter(
    prefix="/characters",
    tags=["characters"]
)

@router.post("/", response_model=Character, status_code=status.HTTP_201_CREATED)
def create_character(
    character: CharacterBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_character = models.Character(**character.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

@router.get("/", response_model=List[Character])
def read_characters(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search by character name"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Character)
    if search:
        query = query.filter(models.Character.name.ilike(f"%{search}%"))
    characters = query.offset(skip).limit(limit).all()
    return characters

@router.get("/{character_id}", response_model=Character)
def read_character(
    character_id: int,
    db: Session = Depends(get_db)
):
    character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@router.put("/{character_id}", response_model=Character)
def update_character(
    character_id: int,
    character: CharacterBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    for key, value in character.dict(exclude_unset=True).items():
        setattr(db_character, key, value)
    
    db.commit()
    db.refresh(db_character)
    return db_character

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    db.delete(db_character)
    db.commit()
    return {"ok": True}