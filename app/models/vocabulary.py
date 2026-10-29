from datetime import datetime, date
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.user import User


class VocabularyCard(Base):
    __tablename__ = "vocabulary_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    german_word: Mapped[str] = mapped_column(String(120), nullable=False)
    malayalam_translation: Mapped[str] = mapped_column(String(200), nullable=False)
    example_sentence: Mapped[str | None] = mapped_column(Text)
    cefr_level: Mapped[str] = mapped_column(String(3), nullable=False)  # A1, A2, B1 …
    topic_tag: Mapped[str | None] = mapped_column(String(60))

    progress: Mapped[list["UserProgress"]] = relationship(back_populates="card", cascade="all, delete-orphan")


class UserProgress(Base):
    """FSRS-inspired card state per user."""

    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("vocabulary_cards.id"), nullable=False)

    # FSRS state
    stability: Mapped[float] = mapped_column(Float, default=1.0)
    difficulty: Mapped[float] = mapped_column(Float, default=5.0)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=1)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    last_reviewed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="progress")
    card: Mapped["VocabularyCard"] = relationship(back_populates="progress")
