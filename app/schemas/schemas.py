from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import List, Optional

# Base Schemas (for creation/update)
class UserBase(BaseModel):
    username: str
    email: EmailStr

class StudioBase(BaseModel):
    name: str
    country: Optional[str] = None
    founded_year: Optional[int] = None

class AnimeBase(BaseModel):
    title: str
    japanese_title: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    synopsis: Optional[str] = None
    episodes_total: Optional[int] = None
    release_date: Optional[date] = None
    end_date: Optional[date] = None
    studio_id: Optional[int] = None
    cover_url: Optional[str] = None

class EpisodeBase(BaseModel):
    anime_id: int
    episode_number: int
    title: Optional[str] = None
    duration_minutes: Optional[int] = None
    air_date: Optional[date] = None

class UserAnimeProgressBase(BaseModel):
    user_id: int
    anime_id: int
    episodes_watched: Optional[int] = 0
    status: Optional[str] = None # e.g., 'Watching', 'Completed', 'On Hold', 'Dropped', 'Plan to Watch'
    score: Optional[int] = None # 1-10

class GenreBase(BaseModel):
    name: str

class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class VoiceActorBase(BaseModel):
    name: str
    nationality: Optional[str] = None
    birthdate: Optional[date] = None

class UserFavoriteBase(BaseModel):
    user_id: int
    anime_id: Optional[int] = None
    character_id: Optional[int] = None


# Schemas for creating (with password for user)
class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


# Schemas for relationships
class GenreInDB(GenreBase):
    id: int
    class Config:
        orm_mode = True

class StudioInDB(StudioBase):
    id: int
    class Config:
        orm_mode = True

class AnimeGenre(BaseModel):
    genre_id: int
    class Config:
        orm_mode = True

class AnimeCharacterRole(BaseModel):
    character_id: int
    role: str
    class Config:
        orm_mode = True

class CharacterVoiceActorLanguage(BaseModel):
    voice_actor_id: int
    language: str
    class Config:
        orm_mode = True


# Response Schemas (include id and other DB generated fields)
class User(UserBase):
    id: int
    created_at: datetime
    # user_anime_progress: List["UserAnimeProgress"] = []
    # user_favorites: List["UserFavorite"] = []

    class Config:
        orm_mode = True

class Studio(StudioBase):
    id: int
    # anime: List["Anime"] = []

    class Config:
        orm_mode = True

class Character(CharacterBase):
    id: int
    # anime: List["Anime"] = []
    # voice_actors: List["VoiceActor"] = []
    # user_favorites: List["UserFavorite"] = []

    class Config:
        orm_mode = True

class VoiceActor(VoiceActorBase):
    id: int
    # characters: List["Character"] = []

    class Config:
        orm_mode = True

class Episode(EpisodeBase):
    id: int

    class Config:
        orm_mode = True

class Anime(AnimeBase):
    id: int
    studio: Optional[StudioInDB] = None
    genres: List[GenreInDB] = []
    # episodes: List[Episode] = [] # Not usually returned in anime list
    # characters: List[Character] = []
    
    class Config:
        orm_mode = True

class UserAnimeProgress(UserAnimeProgressBase):
    id: int
    last_updated: datetime

    class Config:
        orm_mode = True

class Genre(GenreBase):
    id: int
    # anime: List[AnimeBase] = []

    class Config:
        orm_mode = True

class UserFavorite(UserFavoriteBase):
    id: int
    created_at: datetime
    anime: Optional["AnimeInFavorite"] = None
    character: Optional["CharacterInFavorite"] = None

    class Config:
        orm_mode = True

# Simplified schemas for nested favorite data to avoid circular dependencies
class AnimeInFavorite(BaseModel):
    id: int
    title: str
    cover_url: Optional[str] = None
    status: Optional[str] = None
    episodes_total: Optional[int] = None

    class Config:
        orm_mode = True

class CharacterInFavorite(BaseModel):
    id: int
    name: str
    image_url: Optional[str] = None

    class Config:
        orm_mode = True

# Update forward references
UserFavorite.update_forward_refs()

# JWT Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None