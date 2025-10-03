from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models import Student
from ..schemas import StudentCreate, StudentOut

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/", response_model=StudentOut, status_code=201)
def create_student(student: StudentCreate, session: Session = Depends(get_session)):
    # Создаем объект модели из схемы
    db_student = Student(**student.dict())
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student

@router.get("/{student_id}", response_model=StudentOut)
def get_student(student_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    return student