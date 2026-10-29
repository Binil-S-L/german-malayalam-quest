"""Seed a demo user with UserProgress entries so the SRS endpoint returns data."""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.user import User
from app.models.vocabulary import UserProgress, VocabularyCard


def seed_demo(db: Session) -> None:
    if db.query(User).filter_by(username="demo").first():
        print("Demo user already exists, skipping.")
        return

    user = User(username="demo", german_level=2)
    db.add(user)
    db.flush()

    cards = (
        db.query(VocabularyCard).filter(VocabularyCard.cefr_level.in_(["A1", "A2"])).limit(10).all()
    )
    today = date.today()
    for i, card in enumerate(cards):
        db.add(UserProgress(
            user_id=user.id,
            card_id=card.id,
            due_date=today + timedelta(days=i - 5),  # some overdue, some future
        ))

    db.commit()
    print(f"Seeded demo user (id={user.id}) with {len(cards)} progress entries.")


if __name__ == "__main__":
    with SessionLocal() as db:
        seed_demo(db)
