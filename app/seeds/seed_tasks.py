"""Seed task_library and vocabulary_cards from JSON data files."""

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.db import engine, SessionLocal
from app.models.quest import TaskLibrary, TaskType
from app.models.vocabulary import VocabularyCard

DATA_DIR = Path(__file__).parent / "data"


def seed_tasks(db: Session) -> None:
    if db.query(TaskLibrary).count():
        print("task_library already seeded, skipping.")
        return
    tasks = json.loads((DATA_DIR / "tasks.json").read_text())
    for t in tasks:
        db.add(TaskLibrary(
            task_type=TaskType[t["task_type"]],
            title=t["title"],
            description=t["description"],
            url=t.get("url"),
            cefr_level=t["cefr_level"],
            duration_minutes=t.get("duration_minutes"),
        ))
    db.commit()
    print(f"Seeded {len(tasks)} tasks.")


def seed_vocabulary(db: Session) -> None:
    if db.query(VocabularyCard).count():
        print("vocabulary_cards already seeded, skipping.")
        return
    cards = json.loads((DATA_DIR / "vocabulary.json").read_text())
    for c in cards:
        db.add(VocabularyCard(
            german_word=c["german_word"],
            malayalam_translation=c["malayalam_translation"],
            example_sentence=c.get("example_sentence"),
            cefr_level=c["cefr_level"],
            topic_tag=c.get("topic_tag"),
        ))
    db.commit()
    print(f"Seeded {len(cards)} vocabulary cards.")


if __name__ == "__main__":
    with SessionLocal() as db:
        seed_tasks(db)
        seed_vocabulary(db)
