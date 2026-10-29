from datetime import date, datetime

from pydantic import BaseModel


class CardOut(BaseModel):
    id: int
    german_word: str
    malayalam_translation: str
    example_sentence: str | None
    cefr_level: str
    topic_tag: str | None
    due_date: date
    interval_days: int
    repetitions: int
    last_reviewed: datetime | None

    model_config = {"from_attributes": True}


class ReviewRequest(BaseModel):
    card_id: int
    rating: int  # 1=Again 2=Hard 3=Good 4=Easy
