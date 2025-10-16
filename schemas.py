from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Optional
from datetime import datetime

class TermBase(BaseModel):
    english_term: str
    target_language_term: str
    transliteration: Optional[str] = None
    example_sentence: Optional[str] = None
    example_sentence_explained: Optional[str] = None
    notes: Optional[str] = None

class TermCreate(TermBase):
    language_id: int

class TermUpdate(BaseModel):
    learned: Optional[bool] = None
    correct_counter: Optional[int] = None

class TermResponse(TermBase):
    id_vocabulary: int
    language_id: int
    learned: bool
    correct_counter: int
    
    model_config = ConfigDict(from_attributes=True)

class FlashcardResponse(BaseModel):
    id_vocabulary: int
    english_term: str
    target_language_term: str
    transliteration: Optional[str] = None
    example_sentence: Optional[str] = None
    example_sentence_explained: Optional[str] = None
    notes: Optional[str] = None
    correct_counter: int
    
    model_config = ConfigDict(from_attributes=True)

class AnswerRequest(BaseModel):
    term_id: int
    user_answer: str
    answer_type: str  # "english" or "arabic"

class AnswerResponse(BaseModel):
    correct: bool
    correct_answer: str
    message: str
