"""directions, skills, plan items, meetings

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-11

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    directions = op.create_table(
        "directions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.bulk_insert(directions, [{"name": "BACK"}, {"name": "FRONT"}, {"name": "QA"}])

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("direction_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["direction_id"], ["directions.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_skills_direction_id"), "skills", ["direction_id"], unique=False)
    op.create_index(op.f("ix_skills_id"), "skills", ["id"], unique=False)

    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("interviewer_id", sa.Integer(), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("meeting_date", sa.DateTime(), nullable=False),
        sa.Column("summary_markdown", sa.Text(), nullable=False),
        sa.Column("files_and_links", sa.ARRAY(sa.String()), nullable=False),
        sa.Column("problem_comment", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["interviewer_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["participant_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meetings_id"), "meetings", ["id"], unique=False)
    op.create_index(op.f("ix_meetings_participant_id"), "meetings", ["participant_id"], unique=False)

    op.create_table(
        "plan_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PLANNED", "COMPLETED", "TRAINING", "PROBLEM", name="skill_status_enum"),
            nullable=False,
        ),
        sa.Column("confirmed_at", sa.Date(), nullable=True),
        sa.Column("problem_comment", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "skill_id", name="uq_plan_items_user_skill"),
    )
    op.create_index(op.f("ix_plan_items_id"), "plan_items", ["id"], unique=False)
    op.create_index(op.f("ix_plan_items_user_id"), "plan_items", ["user_id"], unique=False)

    op.create_table(
        "meeting_assessments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("has_problem", sa.Boolean(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meeting_assessments_id"), "meeting_assessments", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_meeting_assessments_id"), table_name="meeting_assessments")
    op.drop_table("meeting_assessments")
    op.drop_index(op.f("ix_plan_items_user_id"), table_name="plan_items")
    op.drop_index(op.f("ix_plan_items_id"), table_name="plan_items")
    op.drop_table("plan_items")
    sa.Enum(name="skill_status_enum").drop(op.get_bind(), checkfirst=True)
    op.drop_index(op.f("ix_meetings_participant_id"), table_name="meetings")
    op.drop_index(op.f("ix_meetings_id"), table_name="meetings")
    op.drop_table("meetings")
    op.drop_index(op.f("ix_skills_id"), table_name="skills")
    op.drop_index(op.f("ix_skills_direction_id"), table_name="skills")
    op.drop_table("skills")
    op.drop_table("directions")
