from datetime import datetime, date
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.orm import Session

from app.models.quest import TaskLibrary, TaskType
from app.models.user import User
from app.services.quest import get_or_create_daily_quest, complete_ring, DAILY_DRILL_LIMIT
from app.models.quest import RingEnum


def _make_user(db: Session, username="testuser", level=1) -> User:
    u = User(username=username, german_level=level)
    db.add(u)
    db.flush()
    return u


def _make_tasks(db: Session, count=2) -> None:
    for i in range(count):
        db.add(TaskLibrary(
            task_type=TaskType.MEDIA if i % 2 == 0 else TaskType.ACTION,
            title=f"Task {i}",
            description=f"Description {i}",
            cefr_level="A1",
        ))
    db.flush()


class TestGetOrCreateDailyQuest:
    def test_creates_new_quest(self, db: Session):
        _make_tasks(db)
        user = _make_user(db)
        quest = get_or_create_daily_quest(db, user)
        assert quest.id is not None
        assert quest.quest_date == date.today()
        assert quest.user_id == user.id

    def test_returns_same_quest_on_second_call(self, db: Session):
        _make_tasks(db)
        user = _make_user(db, "user2")
        q1 = get_or_create_daily_quest(db, user)
        q2 = get_or_create_daily_quest(db, user)
        assert q1.id == q2.id

    def test_timezone_boundary_uses_injected_now(self, db: Session):
        _make_tasks(db)
        user = _make_user(db, "user3")
        past = datetime(2024, 1, 15, 23, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        quest = get_or_create_daily_quest(db, user, now=past)
        assert quest.quest_date == date(2024, 1, 15)


class TestCompleteRing:
    def test_complete_media_awards_xp(self, db: Session):
        _make_tasks(db)
        user = _make_user(db, "user4")
        quest = get_or_create_daily_quest(db, user)
        xp = complete_ring(db, user, quest, RingEnum.media)
        assert xp > 0
        assert quest.media_complete is True
        assert quest.xp_awarded == xp

    def test_completing_same_ring_twice_awards_zero(self, db: Session):
        _make_tasks(db)
        user = _make_user(db, "user5")
        quest = get_or_create_daily_quest(db, user)
        complete_ring(db, user, quest, RingEnum.action)
        xp2 = complete_ring(db, user, quest, RingEnum.action)
        assert xp2 == 0

    def test_all_complete_true_after_all_rings(self, db: Session):
        _make_tasks(db)
        user = _make_user(db, "user6")
        quest = get_or_create_daily_quest(db, user)
        for ring in [RingEnum.drill, RingEnum.media, RingEnum.action]:
            complete_ring(db, user, quest, ring)
        assert quest.drill_complete
        assert quest.media_complete
        assert quest.action_complete
