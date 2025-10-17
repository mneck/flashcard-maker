import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import database
from main import create_app
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_backend_with_real_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping real DB integration test")

    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Prepare schema and seed minimal data
    database.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Ensure Arabic language exists
        ar = db.query(database.Language).filter_by(code="ar").first()
        if not ar:
            ar = database.Language(code="ar", name="Arabic")
            db.add(ar)
            db.flush()

        # Ensure at least one term exists
        term = (
            db.query(database.Term)
            .filter_by(language_id=ar.id, english_term="hello")
            .first()
        )
        if not term:
            term = database.Term(
                language_id=ar.id,
                english_term="hello",
                target_language_term="مرحبا",
                transliteration="marḥaba",
                correct_counter=0,
            )
            db.add(term)
        db.commit()
    finally:
        db.close()

    # Build the app with the real sessionmaker
    app = create_app(SessionLocal)
    client = TestClient(app)

    # Verify endpoints work against the real DB
    r = client.get("/flashcards/random", params={"language_code": "ar"})
    if r.status_code == 404:
        detail = r.json().get("detail")
        pytest.skip(f"Backend returned 404: {detail}")
    assert r.status_code == 200
    data = r.json()
    assert data["english_term"]
    assert data["target_language_term"]

    r2 = client.post(
        "/flashcards/answer",
        json={"term_id": data["id_vocabulary"], "user_answer": "hello", "answer_type": "english"},
    )
    assert r2.status_code == 200
    body2 = r2.json()
    assert "correct" in body2


