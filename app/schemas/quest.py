from datetime import date

from pydantic import BaseModel, computed_field

from app.models.quest import RingEnum


class TaskOut(BaseModel):
    id: int
    task_type: str
    title: str
    description: str
    url: str | None
    cefr_level: str
    duration_minutes: int | None
    ring: RingEnum

    model_config = {"from_attributes": True}


class DailyQuestOut(BaseModel):
    id: int
    user_id: int
    quest_date: date
    drill_complete: bool
    media_complete: bool
    action_complete: bool
    xp_awarded: int
    tasks: list[TaskOut]

    @computed_field
    @property
    def all_complete(self) -> bool:
        return self.drill_complete and self.media_complete and self.action_complete

    model_config = {"from_attributes": True}


class CompleteRingRequest(BaseModel):
    ring: RingEnum


class CompleteRingResponse(BaseModel):
    quest: DailyQuestOut
    xp_gained: int
