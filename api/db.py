from sqlmodel import SQLModel, Session, create_engine
import os


DATABASE_URL = os.getenv("DATABASE_URL","postgresql://postgres:postgres@db:5432/postgres")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
