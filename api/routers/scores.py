from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models import Student, Score
from ..schemas import ScoreCreate, ScoreOut

router = APIRouter(prefix="/students/{student_id}/scores", tags=["scores"])

@router.post("/", response_model=ScoreOut)
def upsert_score(student_id: int, payload: ScoreCreate, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")

    # Поиск существующего результата
    statement = select(Score).where(Score.student_id == student_id, Score.subject == payload.subject)
    score = session.exec(statement).first()

    if score:
        score.score = payload.score
    else:
        score = Score(subject=payload.subject, score=payload.score, student_id=student_id)
        session.add(score)

    session.commit()
    session.refresh(score)
    return score

@router.get("/", response_model=list[ScoreOut])
def list_scores(student_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    return student.scores