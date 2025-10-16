import os
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("message") == "Flashcards API is running!"


def test_random_flashcard(client):
    r = client.get("/flashcards/random", params={"language_code": "ar"})
    assert r.status_code == 200
    body = r.json()
    assert body["english_term"] == "hello"
    assert body["target_language_term"] == "مرحبا"


def test_submit_answer_correct_increments(client):
    r = client.get("/flashcards/random", params={"language_code": "ar"})
    assert r.status_code == 200
    card = r.json()
    term_id = card["id_vocabulary"]
    r2 = client.post(
        "/flashcards/answer",
        json={"term_id": term_id, "user_answer": "hello", "answer_type": "english"},
    )
    assert r2.status_code == 200
    assert r2.json()["correct"] is True


