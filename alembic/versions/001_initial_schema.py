"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-10-29
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False, unique=True),
        sa.Column("german_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "vocabulary_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("german_word", sa.String(120), nullable=False),
        sa.Column("malayalam_translation", sa.String(200), nullable=False),
        sa.Column("example_sentence", sa.Text()),
        sa.Column("cefr_level", sa.String(3), nullable=False),
        sa.Column("topic_tag", sa.String(60)),
    )

    op.create_table(
        "user_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("card_id", sa.Integer(), sa.ForeignKey("vocabulary_cards.id"), nullable=False),
        sa.Column("stability", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("difficulty", sa.Float(), nullable=False, server_default="5.0"),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("repetitions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_reviewed", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    task_type_enum = sa.Enum("MEDIA", "ACTION", name="tasktype")
    task_type_enum.create(op.get_bind())
    ring_enum = sa.Enum("drill", "media", "action", name="ringenum")
    ring_enum.create(op.get_bind())

    op.create_table(
        "task_library",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_type", sa.Enum("MEDIA", "ACTION", name="tasktype"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("url", sa.String(500)),
        sa.Column("cefr_level", sa.String(3), nullable=False),
        sa.Column("duration_minutes", sa.Integer()),
    )

    op.create_table(
        "daily_quests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("quest_date", sa.Date(), nullable=False),
        sa.Column("drill_complete", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("media_complete", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("action_complete", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("xp_awarded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "quest_date", name="uq_user_quest_date"),
    )

    op.create_table(
        "quest_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("quest_id", sa.Integer(), sa.ForeignKey("daily_quests.id"), nullable=False),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("task_library.id"), nullable=False),
        sa.Column("ring", sa.Enum("drill", "media", "action", name="ringenum"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("quest_tasks")
    op.drop_table("daily_quests")
    op.drop_table("task_library")
    op.drop_table("user_progress")
    op.drop_table("vocabulary_cards")
    op.drop_table("users")
    sa.Enum(name="ringenum").drop(op.get_bind())
    sa.Enum(name="tasktype").drop(op.get_bind())
