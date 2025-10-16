#!/usr/bin/env python3
"""
Data migration script to populate the database from CSV
Run this after setting up the database schema
"""

import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, Language, Term, create_tables

def migrate_data():
    """Migrate data from CSV to database"""
    # Load env for PROJECT_ROOT, etc.
    load_dotenv()
    project_root = os.getenv("PROJECT_ROOT", "")
    csv_path = os.path.join(project_root, "output.csv") if project_root else "output.csv"

    # Create tables
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Create Arabic language entry
        arabic_lang = db.query(Language).filter(Language.code == "ar").first()
        if not arabic_lang:
            arabic_lang = Language(code="ar", name="Arabic")
            db.add(arabic_lang)
            db.commit()
            db.refresh(arabic_lang)
        
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Map CSV columns to database columns
        for _, row in df.iterrows():
            # Skip rows with NaN values in required fields
            if pd.isna(row["Words (English)"]) or pd.isna(row["Word (Arabic script)"]):
                continue
                
            # Check if term already exists
            existing_term = db.query(Term).filter(
                Term.english_term == row["Words (English)"],
                Term.target_language_term == row["Word (Arabic script)"]
            ).first()
            
            if not existing_term:
                term = Term(
                    language_id=arabic_lang.id,
                    english_term=str(row["Words (English)"]),
                    target_language_term=str(row["Word (Arabic script)"]),
                    transliteration=str(row.get("Word (Arabic with Roman characters)")) if not pd.isna(row.get("Word (Arabic with Roman characters)")) else None,
                    example_sentence=str(row.get("Sample sentence (Arabic)")) if not pd.isna(row.get("Sample sentence (Arabic)")) else None,
                    example_sentence_explained=str(row.get("Sample sentence explained")) if not pd.isna(row.get("Sample sentence explained")) else None,
                    notes=str(row.get("Notes")) if not pd.isna(row.get("Notes")) else None,
                    learned=bool(row.get("Learned", 0)),
                    correct_counter=int(row.get("Correct Counter", 0))
                )
                db.add(term)
        
        db.commit()
        print(f"Successfully migrated {len(df)} terms to database")
        
    except Exception as e:
        db.rollback()
        print(f"Error migrating data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_data()
