
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class StudentCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)

class StudentOut(BaseModel):
    id: int
    first_name: str
    last_name: str

    class Config:
        from_attributes = True  # Замените orm_mode для Pydantic v2


class ScoreCreate(BaseModel):
    subject: str = Field(..., min_length=1, max_length=50)
    score: int = Field(..., ge=0, le=100)  # от 0 до 100 включительно

class ScoreOut(BaseModel):
    id: int
    subject: str
    score: int
    student_id: int

    class Config:
        from_attributes = True