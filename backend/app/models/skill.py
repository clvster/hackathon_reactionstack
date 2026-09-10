from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# Статусы в изучении навыков сотрудником
class SkillStatusEnum(str, Enum):
    PLANNED = "PLANNED"       # Запланирован к изучению
    CONFIRMED = "CONFIRMED"   # Успешно подтвержден на 1:1 встрече
    TRAINING = "IN TRAINING"  # В процессе обучения
    PROBLEM = "PROBLEM"       # По навыку зафиксирована проблема

# --- Блок Справочника Скиллов ---

class SkillBase(BaseModel):
    """Базовые поля скилла, привязанные к структуре подразделений"""
    name: str = Field(..., min_length=2, max_length=100, description="Название навыка")
    department_id: int = Field(..., gt=0, description="ID подразделения (отдела)")

class SkillCreate(SkillBase):
    #  Схема для создания нового скилла (доступно только root/Руководителю)
    pass

class SkillRead(SkillBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- Блок Годового плана развития ---

class PlanItemCreate(BaseModel):
    #  Схема для добавления навыка в личный план сотрудника
    skill_id: int = Field(..., description="ID подключаемого скилла из справочника")
    target_date: date = Field(..., description="Плановая дата, до которой нужно подтвердить готовность к обучению")

class PlanItemRead(BaseModel):
    #  Схема ответа: как скилл выглядит внутри годового плана сотрудника
    id: int
    skill: SkillRead
    target_date: date
    status: SkillStatusEnum
    confirmed_at: Optional[date] = Field(None, description="Фактическая дата подтверждения готовности к обучению")
    problem_comment: Optional[str] = Field(None, description="Комментарий к проблеме (если статус PROBLEM)")
    model_config = ConfigDict(from_attributes=True)