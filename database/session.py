import os
from sqlmodel import SQLModel, create_engine, Session

# Fallback to SQLite if no DATABASE_URL environment variable is provided
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clinicguard.db")

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session