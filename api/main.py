from fastapi import FastAPI
from sqlmodel import SQLModel
from .db import engine
from .routers import students, scores

app = FastAPI(title="EGE Scores API")

# создаём таблицы при старте
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(students.router)
app.include_router(scores.router)
