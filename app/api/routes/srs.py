from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User
from app.schemas.srs import CardOut, ReviewRequest
from app.services import srs as srs_svc

router = APIRouter()


def _get_user(user_id: int, db: Session) -> User:
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/srs/due-cards/{user_id}", response_model=list[CardOut])
def get_due_cards(user_id: int, db: Session = Depends(get_db)):
    user = _get_user(user_id, db)
    rows = srs_svc.get_due_cards(db, user)
    result = []
    for p in rows:
        c = p.card
        result.append(CardOut(
            id=c.id,
            german_word=c.german_word,
            malayalam_translation=c.malayalam_translation,
            example_sentence=c.example_sentence,
            cefr_level=c.cefr_level,
            topic_tag=c.topic_tag,
            due_date=p.due_date,
            interval_days=p.interval_days,
            repetitions=p.repetitions,
            last_reviewed=p.last_reviewed,
        ))
    return result


@router.post("/srs/review", status_code=501)
def submit_review(body: ReviewRequest):
    raise HTTPException(status_code=501, detail="SRS review scheduling not yet implemented")
