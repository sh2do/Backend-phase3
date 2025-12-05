from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from ..schemas.schemas import Anime, AnimeBase, UserAnimeProgress, UserAnimeProgressBase
from ..models import models
from ..database import get_db
from ..auth import auth

router = APIRouter(
    prefix="/anime",
    tags=["anime"]
)

@router.post("/", response_model=Anime, status_code=status.HTTP_201_CREATED)
def create_anime(
    anime: AnimeBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Check if studio exists
    if anime.studio_id:
        studio = db.query(models.Studio).filter(models.Studio.id == anime.studio_id).first()
        if not studio:
            raise HTTPException(status_code=404, detail="Studio not found")

    db_anime = models.Anime(**anime.dict())
    db.add(db_anime)
    db.commit()
    db.refresh(db_anime)
    return db_anime

@router.get("/", response_model=List[Anime])
def read_anime_list(
    skip: int = 0,
    limit: int = 100,
    genre_name: Optional[str] = Query(None, description="Filter by genre name"),
    status: Optional[str] = Query(None, description="Filter by anime status"),
    search: Optional[str] = Query(None, description="Search by anime title or japanese title"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Anime).options(joinedload(models.Anime.studio)).options(joinedload(models.Anime.genres))

    if genre_name:
        query = query.join(models.Anime.genres).filter(models.Genre.name == genre_name)
    if status:
        query = query.filter(models.Anime.status == status)
    if search:
        query = query.filter(
            (models.Anime.title.ilike(f"%{search}%")) |
            (models.Anime.japanese_title.ilike(f"%{search}%"))
        )
    
    anime_list = query.offset(skip).limit(limit).all()
    return anime_list

@router.get("/{anime_id}", response_model=Anime)
def read_anime(
    anime_id: int,
    db: Session = Depends(get_db)
):
    anime = db.query(models.Anime).options(joinedload(models.Anime.studio)).options(joinedload(models.Anime.genres)).filter(models.Anime.id == anime_id).first()
    if anime is None:
        raise HTTPException(status_code=404, detail="Anime not found")
    return anime

@router.put("/{anime_id}", response_model=Anime)
def update_anime(
    anime_id: int,
    anime: AnimeBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if db_anime is None:
        raise HTTPException(status_code=404, detail="Anime not found")
    
    # Check if studio exists if provided
    if anime.studio_id:
        studio = db.query(models.Studio).filter(models.Studio.id == anime.studio_id).first()
        if not studio:
            raise HTTPException(status_code=404, detail="Studio not found")

    for key, value in anime.dict(exclude_unset=True).items():
        setattr(db_anime, key, value)
    
    db.commit()
    db.refresh(db_anime)
    return db_anime

@router.delete("/{anime_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_anime(
    anime_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if db_anime is None:
        raise HTTPException(status_code=404, detail="Anime not found")
    
    db.delete(db_anime)
    db.commit()
    return {"ok": True}

@router.post("/{anime_id}/genres/{genre_id}", response_model=Anime)
def add_genre_to_anime(
    anime_id: int,
    genre_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if not db_anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    
    db_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not db_genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    
    if db_genre not in db_anime.genres:
        db_anime.genres.append(db_genre)
        db.commit()
        db.refresh(db_anime)
    return db_anime

@router.delete("/{anime_id}/genres/{genre_id}", response_model=Anime)
def remove_genre_from_anime(
    anime_id: int,
    genre_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if not db_anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    
    db_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not db_genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    
    if db_genre in db_anime.genres:
        db_anime.genres.remove(db_genre)
        db.commit()
        db.refresh(db_anime)
    return db_anime

@router.post("/{anime_id}/characters/{character_id}", response_model=Anime)
def add_character_to_anime(
    anime_id: int,
    character_id: int,
    role: str = Query(..., description="Role of the character in the anime (e.g., Main, Supporting)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if not db_anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Check if relationship already exists
    existing_relation = db.query(models.anime_characters).filter_by(anime_id=anime_id, character_id=character_id).first()
    if existing_relation:
        raise HTTPException(status_code=400, detail="Character already associated with this anime")

    # Correct way to add association with extra data
    insert_stmt = models.anime_characters.insert().values(
        anime_id=anime_id,
        character_id=character_id,
        role=role
    )
    db.execute(insert_stmt)
    db.commit()
    
    # Refresh the relationship to show the new character
    db.refresh(db_anime)
    
    return db_anime


@router.delete("/{anime_id}/characters/{character_id}", response_model=Anime)
def remove_character_from_anime(
    anime_id: int,
    character_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_anime = db.query(models.Anime).filter(models.Anime.id == anime_id).first()
    if not db_anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    
    db_character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if db_character in db_anime.characters:
        db_anime.characters.remove(db_character)
        db.commit()
        db.refresh(db_anime)
    return db_anime


@router.get("/{anime_id}/progress/{user_id}", response_model=UserAnimeProgress)
def get_user_anime_progress(
    anime_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this user's progress")
    
    progress = db.query(models.UserAnimeProgress).filter(
        models.UserAnimeProgress.user_id == user_id,
        models.UserAnimeProgress.anime_id == anime_id
    ).first()
    
    if progress is None:
        # Create a default progress entry if none exists
        new_progress = models.UserAnimeProgress(user_id=user_id, anime_id=anime_id, episodes_watched=0, status="Plan to Watch", score=None)
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        return new_progress
    
    return progress

@router.post("/{anime_id}/progress", response_model=UserAnimeProgress)
def update_user_anime_progress(
    anime_id: int,
    progress_update: UserAnimeProgressBase, # Only allow specific fields to be updated
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if progress_update.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user's progress")
    
    progress = db.query(models.UserAnimeProgress).filter(
        models.UserAnimeProgress.user_id == current_user.id,
        models.UserAnimeProgress.anime_id == anime_id
    ).first()

    if progress is None:
        # Create new progress entry
        db_progress = models.UserAnimeProgress(
            user_id=current_user.id,
            anime_id=anime_id,
            episodes_watched=progress_update.episodes_watched,
            status=progress_update.status,
            score=progress_update.score
        )
        db.add(db_progress)
        db.commit()
        db.refresh(db_progress)
        return db_progress
    else:
        # Update existing progress entry
        for key, value in progress_update.dict(exclude_unset=True).items():
            setattr(progress, key, value)
        
        db.commit()
        db.refresh(progress)
        return progress