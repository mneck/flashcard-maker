from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, and_
import random
import re
import os
from dotenv import load_dotenv
from database import Term, Language, Base
from schemas import FlashcardResponse, AnswerRequest, AnswerResponse

# Load env
load_dotenv()

def create_app(session_maker: sessionmaker) -> FastAPI:
    app = FastAPI(title="Flashcards API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def get_db():
        db = session_maker()
        try:
            yield db
        finally:
            db.close()

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # ensure tables exist in dev runs
        bind = session_maker.kw.get("bind")  # type: ignore[attr-defined]
        if bind is not None:
            Base.metadata.create_all(bind=bind)
        yield

    app.router.lifespan_context = lifespan

    @app.get("/")
    async def root():
        return {"message": "Flashcards API is running!"}

    @app.get("/flashcards/random", response_model=FlashcardResponse)
    async def get_random_flashcard(
        language_code: str = Query("ar", description="Language code (e.g., 'ar' for Arabic)"),
        learned_only: bool = Query(False, description="Show only learned terms"),
        db: Session = Depends(get_db)
    ):
        language = db.query(Language).filter(Language.code == language_code).first()
        if not language:
            raise HTTPException(status_code=404, detail="Language not found")

        query = db.query(Term).filter(Term.language_id == language.id)
        if learned_only:
            query = query.filter(Term.learned == True)
        else:
            query = query.filter(Term.correct_counter < 3)

        terms = query.all()
        if not terms:
            raise HTTPException(status_code=404, detail="No flashcards available")
        return random.choice(terms)

    @app.post("/flashcards/answer", response_model=AnswerResponse)
    async def submit_answer(
        answer: AnswerRequest,
        db: Session = Depends(get_db)
    ):
        term = db.query(Term).filter(Term.id_vocabulary == answer.term_id).first()
        if not term:
            raise HTTPException(status_code=404, detail="Term not found")

        def normalize_text(text: str) -> str:
            return re.sub(r'\s+', ' ', text.strip().lower())

        user_answer_normalized = normalize_text(answer.user_answer)
        if answer.answer_type == "english":
            correct_answer = term.english_term
        elif answer.answer_type == "arabic":
            correct_answer = term.target_language_term
        else:
            raise HTTPException(status_code=400, detail="Invalid answer_type. Use 'english' or 'arabic'")

        correct = user_answer_normalized == normalize_text(correct_answer)
        if correct:
            term.correct_counter += 1
            if term.correct_counter >= 3:
                term.learned = True
            db.commit()

        message = "Correct! 🎉" if correct else f"Incorrect. The answer is: {correct_answer}"
        return AnswerResponse(correct=correct, correct_answer=correct_answer, message=message)

    @app.get("/flashcards/stats")
    async def get_stats(
        language_code: str = Query("ar", description="Language code"),
        db: Session = Depends(get_db)
    ):
        language = db.query(Language).filter(Language.code == language_code).first()
        if not language:
            raise HTTPException(status_code=404, detail="Language not found")

        total_terms = db.query(Term).filter(Term.language_id == language.id).count()
        learned_terms = db.query(Term).filter(and_(Term.language_id == language.id, Term.learned == True)).count()
        practice_terms = db.query(Term).filter(and_(Term.language_id == language.id, Term.correct_counter < 3)).count()

        return {
            "total_terms": total_terms,
            "learned_terms": learned_terms,
            "practice_terms": practice_terms,
            "progress_percentage": round((learned_terms / total_terms * 100) if total_terms > 0 else 0, 1),
        }

    @app.get("/languages")
    async def get_languages(db: Session = Depends(get_db)):
        languages = db.query(Language).all()
        return [{"id": lang.id, "code": lang.code, "name": lang.name} for lang in languages]

    return app


if __name__ == "__main__":
    import uvicorn
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    app = create_app(SessionLocal)
    port = int(os.getenv("APP_PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)
