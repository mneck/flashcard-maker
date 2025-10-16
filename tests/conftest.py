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
from main import create_app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_sessionmaker():
    # Dedicated SQLite engine for tests; allow cross-thread usage
    test_engine = create_engine(
        "sqlite:///./test_db.sqlite3", connect_args={"check_same_thread": False}
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    yield TestSessionLocal
    database.Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def seed_minimal_data(test_sessionmaker):
    """Seed one language and one term before each test using the test session."""
    bind = test_sessionmaker.kw.get("bind")
    database.Base.metadata.drop_all(bind=bind)
    database.Base.metadata.create_all(bind=bind)
    db = test_sessionmaker()
    try:
        # Tables already recreated above using the test bind

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
def client(seed_minimal_data, test_sessionmaker):
    # Build app with DI using the test sessionmaker
    from fastapi.testclient import TestClient
    app = create_app(test_sessionmaker)
    return TestClient(app)


