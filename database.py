from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Database configuration - PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Language(Base):
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    
    # Relationship
    terms = relationship("Term", back_populates="language")

class Term(Base):
    __tablename__ = "terms"
    
    id_vocabulary = Column(Integer, primary_key=True, index=True)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    english_term = Column(Text, nullable=False)
    target_language_term = Column(Text, nullable=False)
    transliteration = Column(Text)
    example_sentence = Column(Text)
    example_sentence_explained = Column(Text)
    notes = Column(Text)
    learned = Column(Boolean, default=False)
    correct_counter = Column(Integer, default=0)
    
    # Relationship
    language = relationship("Language", back_populates="terms")

class VocabRaw(Base):
    __tablename__ = "vocab_raw"
    
    id = Column(Integer, primary_key=True, index=True)
    english = Column(Text)
    target_script = Column(Text)
    transliteration = Column(Text)
    sample_sentence_target = Column(Text)
    sample_sentence_explained = Column(Text)
    notes = Column(Text)
    learned = Column(Numeric)
    correct_counter = Column(Numeric)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)
