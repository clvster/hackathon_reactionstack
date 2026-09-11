from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class SkillAssessment(BaseModel):
    skill_id: int = Field(..., gt=0, description="ID оцениваемого скилла из справочника")
    is_completed: bool = Field(False, description="Флаг: успешно ли выполнен/подтвержден навык на встрече")
    has_problem: bool = Field(False, description="Флаг: зафиксирована ли проблема по этому навыку")
    comment: Optional[str] = Field(None, max_length=500, description="Комментарий к оценке или описание проблемы")

class MeetingBase(BaseModel):
    participant_id: int = Field(..., gt=0, description="ID сотрудника, с кем проводится встреча")
    meeting_date: datetime = Field(..., description="Дата и время проведения встречи")
    summary_markdown: str = Field(..., min_length=10, description="Подробные итоги встречи в формате Markdown")
    files_and_links: List[str] = Field(default=[], description="Массив ссылок или путей к прикрепленным файлам")

class MeetingCreate(MeetingBase):
    assessments: List[SkillAssessment] = Field(default=[], description="Список оценок навыков, переданных лидом")
    global_problem_comment: Optional[str] = Field(None, max_length=1000, description="Текст общей проблемы по сотруднику в целом")

class MeetingUpdate(BaseModel):
    meeting_date: Optional[datetime] = Field(None, description="Новая дата и время")
    summary_markdown: Optional[str] = Field(None, min_length=10, description="Обновленный текст итогов в Markdown")
    files_and_links: Optional[List[str]] = Field(None, description="Обновленный массив ссылок/файлов")
    assessments: Optional[List[SkillAssessment]] = Field(None, description="Обновленный список оценок навыков")
    global_problem_comment: Optional[str] = Field(None, max_length=1000, description="Обновленный текст общей проблемы")

class MeetingRead(MeetingBase):
    id: int = Field(..., description="ID встречи из базы данных")
    interviewer_id: int = Field(..., gt=0, description="ID руководителя, который провел встречу")

    model_config = ConfigDict(from_attributes=True)
