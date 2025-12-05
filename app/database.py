from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # Potentially useful for testing with SQLite
import os
from dotenv import load_dotenv



# Original database URL from environment
_SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./default.db")

# These will be set by the initial call to configure_db
engine = None
SessionLocal = None

Base = declarative_base()

def configure_db(db_url: str = None):
    global engine, SessionLocal
    
    if db_url is None:
        db_url = _SQLALCHEMY_DATABASE_URL
    
    # Allow overriding connect_args and poolclass for SQLite testing
    connect_args = {}
    poolclass = None
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        poolclass = StaticPool
        
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        poolclass=poolclass
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()