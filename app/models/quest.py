import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.user import User


class RingEnum(enum.StrEnum):
    drill = "drill"
    media = "media"
    action = "action"


class TaskType(enum.StrEnum):
    MEDIA = "MEDIA"
    ACTION = "ACTION"


class TaskLibrary(Base):
    __tablename__ = "task_library"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_type: Mapped[TaskType] = mapped_column(SAEnum(TaskType), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str | None] = mapped_column(String(500))
    cefr_level: Mapped[str] = mapped_column(String(3), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)

    quest_tasks: Mapped[list["QuestTask"]] = relationship(back_populates="task")


class DailyQuest(Base):
    __tablename__ = "daily_quests"
    __table_args__ = (UniqueConstraint("user_id", "quest_date", name="uq_user_quest_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    quest_date: Mapped[date] = mapped_column(Date, nullable=False)
    drill_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    media_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    action_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="quests")
    tasks: Mapped[list["QuestTask"]] = relationship(
        back_populates="quest", cascade="all, delete-orphan"
    )


class QuestTask(Base):
    __tablename__ = "quest_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quest_id: Mapped[int] = mapped_column(Integer, ForeignKey("daily_quests.id"), nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("task_library.id"), nullable=False)
    ring: Mapped[RingEnum] = mapped_column(SAEnum(RingEnum), nullable=False)

    quest: Mapped["DailyQuest"] = relationship(back_populates="tasks")
    task: Mapped["TaskLibrary"] = relationship(back_populates="quest_tasks")
