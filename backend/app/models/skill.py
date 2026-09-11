import enum
from datetime import date
from sqlalchemy import Integer, String, Enum, Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.schemas.skill import SkillStatusEnum

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    direction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("directions.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    plan_items: Mapped[list["PlanItem"]] = relationship("PlanItem", back_populates="skill", cascade="all, delete-orphan")


class PlanItem(Base):
    __tablename__ = "plan_items"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_plan_items_user_skill"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[SkillStatusEnum] = mapped_column(Enum(SkillStatusEnum, name="skill_status_enum"), default=SkillStatusEnum.PLANNED, nullable=False)
    confirmed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    problem_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    skill: Mapped["Skill"] = relationship("Skill", back_populates="plan_items")
