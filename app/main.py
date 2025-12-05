from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv() # Load environment variables early

from .database import engine, configure_db, _SQLALCHEMY_DATABASE_URL
from .models import models
from .routers import auth, users, studios, genres, characters, episodes, anime, favorites

# Configure the database explicitly
configure_db(_SQLALCHEMY_DATABASE_URL)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Anime Collection Tracker API",
    description="API for managing an anime collection, user progress, and related entities.",
    version="0.1.0",
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Common alternative frontend port
    "http://localhost:5173",  # Default Vite frontend port
    "http://localhost:8000",  # For development if frontend runs on a different port or direct access
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(studios.router)
app.include_router(genres.router)
app.include_router(characters.router)
app.include_router(episodes.router)
app.include_router(anime.router)
app.include_router(favorites.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Anime Collection Tracker API!"}