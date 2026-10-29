from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vocabulary import UserProgress, VocabularyCard
from app.models.user import User


def get_due_cards(db: Session, user: User, today: date | None = None) -> list[UserProgress]:
    if today is None:
        today = date.today()
    rows = db.scalars(
        select(UserProgress)
        .where(UserProgress.user_id == user.id, UserProgress.due_date <= today)
        .order_by(UserProgress.due_date)
    ).all()
    return list(rows)
