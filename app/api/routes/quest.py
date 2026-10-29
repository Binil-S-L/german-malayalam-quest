from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User
from app.schemas.quest import CompleteRingRequest, CompleteRingResponse, DailyQuestOut
from app.services import quest as quest_svc

router = APIRouter()


def _get_user(user_id: int, db: Session) -> User:
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/daily-quest/{user_id}", response_model=DailyQuestOut)
def get_daily_quest(user_id: int, db: Session = Depends(get_db)):
    user = _get_user(user_id, db)
    quest = quest_svc.get_or_create_daily_quest(db, user)
    return _quest_with_tasks(quest)


@router.post("/complete/{user_id}", response_model=CompleteRingResponse)
def complete_ring(user_id: int, body: CompleteRingRequest, db: Session = Depends(get_db)):
    user = _get_user(user_id, db)
    quest = quest_svc.get_or_create_daily_quest(db, user)
    xp = quest_svc.complete_ring(db, user, quest, body.ring)
    return CompleteRingResponse(quest=_quest_with_tasks(quest), xp_gained=xp)


def _quest_with_tasks(quest):
    from app.schemas.quest import DailyQuestOut, TaskOut
    tasks = []
    for qt in quest.tasks:
        t = qt.task
        tasks.append(TaskOut(
            id=t.id,
            task_type=t.task_type.value,
            title=t.title,
            description=t.description,
            url=t.url,
            cefr_level=t.cefr_level,
            duration_minutes=t.duration_minutes,
            ring=qt.ring,
        ))
    return DailyQuestOut(
        id=quest.id,
        user_id=quest.user_id,
        quest_date=quest.quest_date,
        drill_complete=quest.drill_complete,
        media_complete=quest.media_complete,
        action_complete=quest.action_complete,
        xp_awarded=quest.xp_awarded,
        tasks=tasks,
    )
