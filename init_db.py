from app.database import Base, engine
from app.models import models # Import models to ensure they are registered with Base.metadata

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created!")