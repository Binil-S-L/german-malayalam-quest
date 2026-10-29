from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.vocabulary import UserProgress, VocabularyCard
from app.services.srs import get_due_cards


def _make_user(db: Session, username="srsuser") -> User:
    u = User(username=username, german_level=1)
    db.add(u)
    db.flush()
    return u


def _make_card(db: Session, word="Hallo") -> VocabularyCard:
    c = VocabularyCard(german_word=word, malayalam_translation="ഹലോ", cefr_level="A1")
    db.add(c)
    db.flush()
    return c


class TestGetDueCards:
    def test_returns_overdue_cards(self, db: Session):
        user = _make_user(db)
        card = _make_card(db)
        p = UserProgress(
            user_id=user.id, card_id=card.id, due_date=date.today() - timedelta(days=1)
        )
        db.add(p)
        db.flush()

        due = get_due_cards(db, user, today=date.today())
        assert len(due) == 1
        assert due[0].card_id == card.id

    def test_excludes_future_cards(self, db: Session):
        user = _make_user(db, "srsuser2")
        card = _make_card(db, "Danke")
        p = UserProgress(
            user_id=user.id, card_id=card.id, due_date=date.today() + timedelta(days=3)
        )
        db.add(p)
        db.flush()

        due = get_due_cards(db, user, today=date.today())
        assert len(due) == 0

    def test_review_endpoint_returns_501(self, client):
        resp = client.post("/api/v1/srs/review", json={"card_id": 1, "rating": 3})
        assert resp.status_code == 501
