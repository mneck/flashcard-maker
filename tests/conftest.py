import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is on sys.path for imports like `import database`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import database  # now resolvable
from main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def test_db_setup():
    # Dedicated SQLite engine for tests; allow cross-thread usage
    test_engine = create_engine(
        "sqlite:///./test_db.sqlite3", connect_args={"check_same_thread": False}
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Monkey-patch the app's DB bindings
    database.engine = test_engine
    database.SessionLocal = TestSessionLocal

    # Create schema once per session
    database.Base.metadata.create_all(bind=test_engine)

    # Override dependency
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[database.get_db] = override_get_db

    yield

    # Clean up
    database.Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def seed_minimal_data():
    """Seed one language and one term before each test using the test session."""
    db = database.SessionLocal()
    try:
        # Ensure clean tables each test
        database.Base.metadata.drop_all(bind=database.engine)
        database.Base.metadata.create_all(bind=database.engine)

        lang = database.Language(code="ar", name="Arabic")
        db.add(lang)
        db.flush()
        term = database.Term(
            language_id=lang.id,
            english_term="hello",
            target_language_term="مرحبا",
            transliteration="marḥaba",
            correct_counter=0,
        )
        db.add(term)
        db.commit()
        yield
    finally:
        db.close()


@pytest.fixture
def client(seed_minimal_data):
    # Ensure seeding ran before creating the client/app
    return TestClient(app)


