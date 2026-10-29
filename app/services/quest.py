from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.quest import DailyQuest, QuestTask, RingEnum, TaskLibrary, TaskType
from app.models.user import User

DAILY_DRILL_LIMIT = 15
XP_PER_RING = 10
TIMEZONE = ZoneInfo("Europe/Berlin")

_RING_COMPLETE_FIELD = {
    RingEnum.drill: "drill_complete",
    RingEnum.media: "media_complete",
    RingEnum.action: "action_complete",
}


def _today(now: datetime | None) -> date:
    if now is None:
        now = datetime.now(tz=TIMEZONE)
    return now.astimezone(TIMEZONE).date()


def _pick_task(
    db: Session, task_type: TaskType, level: int, exclude_ids: list[int]
) -> TaskLibrary | None:
    """Level fallback: exact level → lower. Skips last-7-day tasks when alternatives exist."""
    for lvl in range(level, 0, -1):
        cefr = _level_to_cefr(lvl)
        q = (
            select(TaskLibrary)
            .where(TaskLibrary.task_type == task_type, TaskLibrary.cefr_level == cefr)
        )
        candidates = db.scalars(q).all()
        if not candidates:
            continue
        fresh = [t for t in candidates if t.id not in exclude_ids]
        pool = fresh if fresh else candidates
        if pool:
            return pool[0]
    return None


def _level_to_cefr(level: int) -> str:
    mapping = {1: "A1", 2: "A1", 3: "A2", 4: "A2", 5: "B1", 6: "B1", 7: "B2", 8: "B2"}
    return mapping.get(level, "A1")


def _recent_task_ids(db: Session, user_id: int, days: int = 7) -> list[int]:
    cutoff = func.current_date() - days
    rows = db.execute(
        select(QuestTask.task_id)
        .join(DailyQuest, DailyQuest.id == QuestTask.quest_id)
        .where(DailyQuest.user_id == user_id, DailyQuest.quest_date >= cutoff)
    ).scalars().all()
    return list(rows)


def get_or_create_daily_quest(db: Session, user: User, now: datetime | None = None) -> DailyQuest:
    today = _today(now)

    existing = db.scalars(
        select(DailyQuest).where(DailyQuest.user_id == user.id, DailyQuest.quest_date == today)
    ).first()
    if existing:
        return existing

    quest = DailyQuest(user_id=user.id, quest_date=today)
    db.add(quest)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return db.scalars(
            select(DailyQuest).where(DailyQuest.user_id == user.id, DailyQuest.quest_date == today)
        ).one()

    exclude_ids = _recent_task_ids(db, user.id)

    for task_type, ring in [(TaskType.MEDIA, RingEnum.media), (TaskType.ACTION, RingEnum.action)]:
        task = _pick_task(db, task_type, user.german_level, exclude_ids)
        if task:
            db.add(QuestTask(quest_id=quest.id, task_id=task.id, ring=ring))
            exclude_ids.append(task.id)

    db.commit()
    db.refresh(quest)
    return quest


def complete_ring(db: Session, user: User, quest: DailyQuest, ring: RingEnum) -> int:
    field = _RING_COMPLETE_FIELD[ring]
    if getattr(quest, field):
        return 0

    setattr(quest, field, True)
    xp = XP_PER_RING
    quest.xp_awarded += xp
    user.xp += xp
    db.commit()
    db.refresh(quest)
    return xp
