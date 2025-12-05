from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Date, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

# Association tables for many-to-many relationships
anime_genres = Table(
    'anime_genres',
    Base.metadata,
    Column('anime_id', Integer, ForeignKey('anime.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)

anime_characters = Table(
    'anime_characters',
    Base.metadata,
    Column('anime_id', Integer, ForeignKey('anime.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('role', String) # e.g., 'Main', 'Supporting'
)

character_voice_actors = Table(
    'character_voice_actors',
    Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('voice_actor_id', Integer, ForeignKey('voice_actors.id'), primary_key=True),
    Column('language', String) # e.g., 'Japanese', 'English'
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user_anime_progress = relationship("UserAnimeProgress", back_populates="user")
    user_favorites = relationship("UserFavorite", back_populates="user")


class Studio(Base):
    __tablename__ = "studios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    country = Column(String)
    founded_year = Column(Integer)

    # Relationships
    anime = relationship("Anime", back_populates="studio")


class Anime(Base):
    __tablename__ = "anime"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    japanese_title = Column(String, index=True)
    status = Column(String) # e.g., 'Airing', 'Finished Airing', 'Not yet aired'
    type = Column(String) # e.g., 'TV', 'Movie', 'OVA', 'ONA', 'Special'
    synopsis = Column(Text)
    episodes_total = Column(Integer)
    release_date = Column(Date)
    end_date = Column(Date)
    cover_url = Column(String)

    studio_id = Column(Integer, ForeignKey("studios.id"))

    # Relationships
    studio = relationship("Studio", back_populates="anime")
    episodes = relationship("Episode", back_populates="anime")
    genres = relationship("Genre", secondary=anime_genres, back_populates="anime")
    characters = relationship("Character", secondary=anime_characters, back_populates="anime")
    user_anime_progress = relationship("UserAnimeProgress", back_populates="anime")
    user_favorites = relationship("UserFavorite", back_populates="anime")


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    anime_id = Column(Integer, ForeignKey("anime.id"))
    episode_number = Column(Integer, nullable=False)
    title = Column(String)
    duration_minutes = Column(Integer)
    air_date = Column(Date)

    # Relationships
    anime = relationship("Anime", back_populates="episodes")


class UserAnimeProgress(Base):
    __tablename__ = "user_anime_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    anime_id = Column(Integer, ForeignKey("anime.id"))
    episodes_watched = Column(Integer, default=0)
    status = Column(String) # e.g., 'Watching', 'Completed', 'On Hold', 'Dropped', 'Plan to Watch'
    score = Column(Integer) # 1-10
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="user_anime_progress")
    anime = relationship("Anime", back_populates="user_anime_progress")


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # Relationships
    anime = relationship("Anime", secondary=anime_genres, back_populates="genres")


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    image_url = Column(String)

    # Relationships
    anime = relationship("Anime", secondary=anime_characters, back_populates="characters")
    voice_actors = relationship("VoiceActor", secondary=character_voice_actors, back_populates="characters")
    user_favorites = relationship("UserFavorite", back_populates="character")


class VoiceActor(Base):
    __tablename__ = "voice_actors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    nationality = Column(String)
    birthdate = Column(Date)

    # Relationships
    characters = relationship("Character", secondary=character_voice_actors, back_populates="voice_actors")


class UserFavorite(Base):
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    anime_id = Column(Integer, ForeignKey("anime.id"), nullable=True) # Either anime or character can be favorited
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="user_favorites")
    anime = relationship("Anime", back_populates="user_favorites")
    character = relationship("Character", back_populates="user_favorites")