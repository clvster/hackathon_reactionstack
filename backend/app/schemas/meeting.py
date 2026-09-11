from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SkillAssessment(BaseModel):
    skill_id: int = Field(..., gt=0, description="ID скилла из справочника")
    is_completed: bool = Field(False, description="Скилл подтверждён на встрече")
    has_problem: bool = Field(False, description="По скиллу зафиксирована проблема")
    comment: Optional[str] = Field(None, max_length=500, description="Комментарий к оценке или описание проблемы")


class AssessmentRead(BaseModel):
    id: int
    skill_id: int
    is_completed: bool
    has_problem: bool
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MeetingBase(BaseModel):
    participant_id: int = Field(..., gt=0, description="ID сотрудника, с которым проводится встреча")
    meeting_date: datetime = Field(..., description="Дата и время встречи")
    summary_markdown: str = Field(..., min_length=10, description="Итоги встречи в Markdown")
    files_and_links: List[str] = Field(default=[], description="Ссылки и прикреплённые файлы")


class MeetingCreate(MeetingBase):
    assessments: List[SkillAssessment] = Field(default=[], description="Оценки скиллов на встрече")
    global_problem_comment: Optional[str] = Field(None, max_length=1000, description="Проблема по сотруднику в целом")


class MeetingUpdate(BaseModel):
    meeting_date: Optional[datetime] = None
    summary_markdown: Optional[str] = Field(None, min_length=10)
    files_and_links: Optional[List[str]] = None
    assessments: Optional[List[SkillAssessment]] = None
    global_problem_comment: Optional[str] = Field(None, max_length=1000)


class MeetingRead(MeetingBase):
    id: int
    interviewer_id: int
    problem_comment: Optional[str] = None
    assessments: List[AssessmentRead] = []

    model_config = ConfigDict(from_attributes=True)
