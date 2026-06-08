import os
from pathlib import Path
from sqlmodel import create_engine, SQLModel

_default_db = str(Path(__file__).resolve().parent / "bloomberg.db")
DATABASE_URL = f"sqlite:///{os.getenv('DB_PATH', _default_db)}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
