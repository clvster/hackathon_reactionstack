from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class SkillAssessment(BaseModel):
    #  Схема оценки конкретного скилла в рамках одной встречи 1:1
    skill_id: int = Field(..., gt=0, description="ID оцениваемого скилла из справочника")
    is_confirmed: bool = Field(False, description="Флаг: успешно ли сдан/подтвержден навык на встрече")
    has_problem: bool = Field(False, description="Флаг: зафиксирована ли проблема по этому навыку")
    comment: Optional[str] = Field(None, max_length=500, description="Комментарий к оценке или описание проблемы")

# --- Схемы для API встреч ---

class MeetingBase(BaseModel):
    #  Базовые поля протокола встречи 1:1
    participant_id: int = Field(..., gt=0, description="ID сотрудника, с кем проводится встреча")
    meeting_date: datetime = Field(..., description="Дата и время проведения встречи")
    summary_markdown: str = Field(..., min_length=10, description="Подробные итоги встречи в формате Markdown")
    files_and_links: List[str] = Field(default=[], description="Массив ссылок или путей к прикрепленным файлам")

class MeetingCreate(MeetingBase):
    #  Схема для создания нового протокола встречи (входящие данные с фронтенда) УДАЛИТЬ КОММЕНТАРИЙ!!!!!!!!!!
    # Список оцениваемых на встрече навыков
    assessments: List[SkillAssessment] = Field(default=[], description="Список оценок навыков, переданных лидом")
    # Текст общей проблемы по сотруднику не обязательно
    global_problem_comment: Optional[str] = Field(None, max_length=1000, description="Текст общей проблемы по сотруднику в целом")

class MeetingUpdate(BaseModel):
    """Схема для редактирования протокола встречи (доступно Руководителю).
    Все поля необязательны, обновляется только то, что прислал фронтенд. УДАЛИТЬ КОММЕНТАРИЙ!!!!!!!!!!!!!"""
    meeting_date: Optional[datetime] = Field(None, description="Новая дата и время")
    summary_markdown: Optional[str] = Field(None, min_length=10, description="Обновленный текст итогов в Markdown")
    files_and_links: Optional[List[str]] = Field(None, description="Обновленный массив ссылок/файлов")
    assessments: Optional[List[SkillAssessment]] = Field(None, description="Обновленный список оценок навыков")
    global_problem_comment: Optional[str] = Field(None, max_length=1000, description="Обновленный текст общей проблемы")

class MeetingRead(MeetingBase):
    #  Схема для возврата информации о встрече (то, что мы отдаем в историю встреч)
    id: int = Field(..., description="ID встречи")
    interviewer_id: int = Field(..., gt=0, description="ID руководителя, который провел встречу")

    # Включаем совместимость с SQLAlchemy моделями твоего коллеги
    model_config = ConfigDict(from_attributes=True)