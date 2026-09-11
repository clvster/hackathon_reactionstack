from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Text, DateTime, Boolean, ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    interviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    participant_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    meeting_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    summary_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    files_and_links: Mapped[list[str]] = mapped_column(ARRAY(String), default=[], nullable=False)

    assessments: Mapped[list["MeetingAssessment"]] = relationship("MeetingAssessment", back_populates="meeting", cascade="all, delete-orphan")


class MeetingAssessment(Base):
    __tablename__ = "meeting_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_problem: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="assessments")
