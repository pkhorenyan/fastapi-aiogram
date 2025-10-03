from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Score(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject: str
    score: int

    student_id: int = Field(foreign_key="student.id")
    student: "Student" = Relationship(back_populates="scores")


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str

    scores: List[Score] = Relationship(back_populates="student")
