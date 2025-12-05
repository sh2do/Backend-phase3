from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas.schemas import Studio, StudioBase
from ..models import models
from ..database import get_db
from ..auth import auth

router = APIRouter(
    prefix="/studios",
    tags=["studios"]
)

@router.post("/", response_model=Studio, status_code=status.HTTP_201_CREATED)
def create_studio(
    studio: StudioBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Only authenticated users can create studios. Add specific role-based authorization if needed.
    db_studio = models.Studio(**studio.dict())
    db.add(db_studio)
    db.commit()
    db.refresh(db_studio)
    return db_studio

@router.get("/", response_model=List[Studio])
def read_studios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    studios = db.query(models.Studio).offset(skip).limit(limit).all()
    return studios

@router.get("/{studio_id}", response_model=Studio)
def read_studio(
    studio_id: int,
    db: Session = Depends(get_db)
):
    studio = db.query(models.Studio).filter(models.Studio.id == studio_id).first()
    if studio is None:
        raise HTTPException(status_code=404, detail="Studio not found")
    return studio

@router.put("/{studio_id}", response_model=Studio)
def update_studio(
    studio_id: int,
    studio: StudioBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_studio = db.query(models.Studio).filter(models.Studio.id == studio_id).first()
    if db_studio is None:
        raise HTTPException(status_code=404, detail="Studio not found")
    
    for key, value in studio.dict(exclude_unset=True).items():
        setattr(db_studio, key, value)
    
    db.commit()
    db.refresh(db_studio)
    return db_studio

@router.delete("/{studio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_studio(
    studio_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_studio = db.query(models.Studio).filter(models.Studio.id == studio_id).first()
    if db_studio is None:
        raise HTTPException(status_code=404, detail="Studio not found")
    
    db.delete(db_studio)
    db.commit()
    return {"ok": True}