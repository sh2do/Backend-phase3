from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas.schemas import Episode, EpisodeBase
from ..models import models
from ..database import get_db
from ..auth import auth

router = APIRouter(
    prefix="/episodes",
    tags=["episodes"]
)

@router.post("/", response_model=Episode, status_code=status.HTTP_201_CREATED)
def create_episode(
    episode: EpisodeBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Ensure the anime exists
    anime = db.query(models.Anime).filter(models.Anime.id == episode.anime_id).first()
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")

    db_episode = models.Episode(**episode.dict())
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return db_episode

@router.get("/anime/{anime_id}", response_model=List[Episode])
def read_episodes_for_anime(
    anime_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Ensure the anime exists
    anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")

    episodes = db.query(models.Episode).filter(models.Episode.anime_id == anime_id).order_by(models.Episode.episode_number).offset(skip).limit(limit).all()
    return episodes

@router.get("/{episode_id}", response_model=Episode)
def read_episode(
    episode_id: int,
    db: Session = Depends(get_db)
):
    episode = db.query(models.Episode).filter(models.Episode.id == episode_id).first()
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode

@router.put("/{episode_id}", response_model=Episode)
def update_episode(
    episode_id: int,
    episode: EpisodeBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_episode = db.query(models.Episode).filter(models.Episode.id == episode_id).first()
    if db_episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    # Ensure the anime_id, if provided, is valid
    if episode.anime_id:
        anime = db.query(models.Anime).filter(models.Anime.id == episode.anime_id).first()
        if not anime:
            raise HTTPException(status_code=404, detail="Anime not found for the provided anime_id")

    for key, value in episode.dict(exclude_unset=True).items():
        setattr(db_episode, key, value)
    
    db.commit()
    db.refresh(db_episode)
    return db_episode

@router.delete("/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_episode(
    episode_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_episode = db.query(models.Episode).filter(models.Episode.id == episode_id).first()
    if db_episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    db.delete(db_episode)
    db.commit()
    return {"ok": True}