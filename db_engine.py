# db_engine.py
import os
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

def get_database_url():
    """
    Build the database URL for Neon from environment variables.
    """
    return URL.create(
        drivername=os.getenv("DB_DRIVER", "postgresql+psycopg2"),
        username=os.getenv("DB_USER", "user"),
        password=os.getenv("DB_PASSWORD", "password"),
        host=os.getenv("DB_HOST", "your‑neon‑host.neon.tech"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "yourdatabase"),
    )

def get_engine(echo: bool = False, pool_size: int = 5, max_overflow: int = 10):
    """
    Create and return a SQLAlchemy Engine for Neon.
    """
    db_url = get_database_url()
    engine = create_engine(
        db_url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        connect_args = {
            "sslmode": os.getenv("DB_SSLMODE", "require")
        }
    )
    return engine

def get_session(engine=None):
    """
    Return a SQLAlchemy ORM Session bound to the engine.
    """
    if engine is None:
        engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

if __name__ == "__main__":
    eng = get_engine(echo=True)
    print("Engine created:", eng)
    sess = get_session(engine=eng)
    print("Session created:", sess)