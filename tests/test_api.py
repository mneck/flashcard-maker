import pytest


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


def test_random_flashcard_unknown_language_returns_404(client):
    r = client.get("/flashcards/random", params={"language_code": "xx"})
    assert r.status_code == 404
    assert r.json().get("detail") == "Language not found"


def test_random_flashcard_learned_only_when_none_available_returns_404(client):
    # Seeded data has 0 learned terms; requesting learned_only should 404
    r = client.get("/flashcards/random", params={"language_code": "ar", "learned_only": True})
    assert r.status_code == 404
    assert r.json().get("detail") in {"No flashcards available", "Language not found"}

