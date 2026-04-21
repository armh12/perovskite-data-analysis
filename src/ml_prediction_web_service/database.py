import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

def expand_env_vars(text: str) -> str:
    if not text:
        return text
    # Support both ${VAR} and $VAR
    return re.sub(r'\$\{([^}]+)\}|\$([a-zA-Z_][a-zA-Z0-9_]*)', 
                  lambda m: os.getenv(m.group(1) or m.group(2), m.group(0)), 
                  text)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/perovskite_db")
DATABASE_URL = expand_env_vars(DATABASE_URL)

# Ensure the URL is synchronous (strip +asyncpg if present)
if "postgresql+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
