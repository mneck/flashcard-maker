from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
import random
import re

import os
from dotenv import load_dotenv
from database import get_db, Term, Language, create_tables
from schemas import FlashcardResponse, AnswerRequest, AnswerResponse, TermResponse

# Load env
load_dotenv()

app = FastAPI(title="Flashcards API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "Flashcards API is running!"}

@app.get("/flashcards/random", response_model=FlashcardResponse)
async def get_random_flashcard(
    language_code: str = Query("ar", description="Language code (e.g., 'ar' for Arabic)"),
    learned_only: bool = Query(False, description="Show only learned terms"),
    db: Session = Depends(get_db)
):
    """Get a random flashcard for practice"""
    
    # Get language
    language = db.query(Language).filter(Language.code == language_code).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    # Build query
    query = db.query(Term).filter(Term.language_id == language.id)
    
    if learned_only:
        query = query.filter(Term.learned == True)
    else:
        # For weekly practice, show terms with correct_counter < 3
        query = query.filter(Term.correct_counter < 3)
    
    # Get random term
    terms = query.all()
    if not terms:
        raise HTTPException(status_code=404, detail="No flashcards available")
    
    term = random.choice(terms)
    return term

@app.post("/flashcards/answer", response_model=AnswerResponse)
async def submit_answer(
    answer: AnswerRequest,
    db: Session = Depends(get_db)
):
    """Submit an answer and get feedback"""
    
    # Get the term
    term = db.query(Term).filter(Term.id_vocabulary == answer.term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    
    # Normalize answers for comparison
    def normalize_text(text: str) -> str:
        return re.sub(r'\s+', ' ', text.strip().lower())
    
    user_answer_normalized = normalize_text(answer.user_answer)
    
    # Check answer based on type
    if answer.answer_type == "english":
        correct_answer = term.english_term
        correct_answer_normalized = normalize_text(correct_answer)
        correct = user_answer_normalized == correct_answer_normalized
    elif answer.answer_type == "arabic":
        correct_answer = term.target_language_term
        correct_answer_normalized = normalize_text(correct_answer)
        correct = user_answer_normalized == correct_answer_normalized
    else:
        raise HTTPException(status_code=400, detail="Invalid answer_type. Use 'english' or 'arabic'")
    
    # Update counter if correct
    if correct:
        term.correct_counter += 1
        # Mark as learned after 3 correct answers
        if term.correct_counter >= 3:
            term.learned = True
        db.commit()
    
    # Prepare response
    message = "Correct! 🎉" if correct else f"Incorrect. The answer is: {correct_answer}"
    
    return AnswerResponse(
        correct=correct,
        correct_answer=correct_answer,
        message=message
    )

@app.get("/flashcards/stats")
async def get_stats(
    language_code: str = Query("ar", description="Language code"),
    db: Session = Depends(get_db)
):
    """Get statistics for the language"""
    
    language = db.query(Language).filter(Language.code == language_code).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")
    
    total_terms = db.query(Term).filter(Term.language_id == language.id).count()
    learned_terms = db.query(Term).filter(
        and_(Term.language_id == language.id, Term.learned == True)
    ).count()
    practice_terms = db.query(Term).filter(
        and_(Term.language_id == language.id, Term.correct_counter < 3)
    ).count()
    
    return {
        "total_terms": total_terms,
        "learned_terms": learned_terms,
        "practice_terms": practice_terms,
        "progress_percentage": round((learned_terms / total_terms * 100) if total_terms > 0 else 0, 1)
    }

@app.get("/languages")
async def get_languages(db: Session = Depends(get_db)):
    """Get all available languages"""
    languages = db.query(Language).all()
    return [{"id": lang.id, "code": lang.code, "name": lang.name} for lang in languages]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)
