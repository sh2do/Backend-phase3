import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import models directly, and the get_db dependency and configure_db function
import app.models.models as models
from app.database import get_db, configure_db, Base
import app.database as database # Import the module to access its global engine

# Use an in-memory SQLite database for testing
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Fixture to provide a TestClient configured with the test database
@pytest.fixture(name="client")
def client_fixture():
    # Configure the database with the test URL
    configure_db(TEST_SQLALCHEMY_DATABASE_URL)
    
    # Create tables for the test database
    # Use the engine from the app.database module which has been configured
    Base.metadata.create_all(bind=database.engine)
    
    # Create a testing session local bound to the test engine
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database.engine)

    # Override the get_db dependency for tests
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    # Import app here to ensure it uses the overridden dependency
    from app.main import app 
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Teardown: drop tables after test is complete
    Base.metadata.drop_all(bind=database.engine)
    app.dependency_overrides.clear() # Clear overrides

def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Anime Collection Tracker API!"}