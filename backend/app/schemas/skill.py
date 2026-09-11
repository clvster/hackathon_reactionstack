from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class SkillStatusEnum(str, Enum):
    PLANNED = "PLANNED"       # Запланирован к изучению
    COMPLETED = "COMPLETED"   # Успешно подтвержден
    TRAINING = "IN TRAINING"  # В процессе обучения
    PROBLEM = "PROBLEM"       # По навыку зафиксирована проблема


class SkillBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Название навыка", examples=["FastAPI & Asyncio"])
    direction_id: int = Field(..., gt=0, description="ID направления (BACK/FRONT/QA) из дерева структуры")

class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Новое название навыка")
    direction_id: Optional[int] = Field(None, gt=0, description="Новый ID направления")

class SkillRead(SkillBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PlanItemCreate(BaseModel):
    skill_id: int = Field(..., description="ID подключаемого скилла из справочника")
    target_date: date = Field(..., description="Плановая дата, до которой нужно подтвердить готовность")

class PlanItemRead(BaseModel):
    id: int
    skill: SkillRead
    target_date: date
    status: SkillStatusEnum
    confirmed_at: Optional[date] = Field(None, description="Фактическая дата выполнения")
    problem_comment: Optional[str] = Field(None, description="Комментарий к проблеме (если статус PROBLEM)")

    model_config = ConfigDict(from_attributes=True)


class PlanItemUpdate(BaseModel):
    target_date: Optional[date] = Field(None, description="Новая плановая дата")
    status: Optional[SkillStatusEnum] = Field(None, description="Новый статус")
    problem_comment: Optional[str] = Field(None, max_length=1000, description="Комментарий к проблеме")
