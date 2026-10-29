from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.vocabulary import UserProgress
    from app.models.quest import DailyQuest


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    german_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    progress: Mapped[list["UserProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    quests: Mapped[list["DailyQuest"]] = relationship(back_populates="user", cascade="all, delete-orphan")
