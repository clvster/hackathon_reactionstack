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
    COMPLETED = "COMPLETED"   # Навык успешно освоен и подтвержден, обучение завершено


class SkillBase(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Название навыка"
    )
    department_id: int = Field(
        ...,
        gt=0,
        description="ID подразделения (отдела) из дерева компании, к которому относится скилл"
    )

class SkillCreate(SkillBase):
    """Схема для создания скилла. Наследует обязательные поля из SkillBase."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "FastAPI & Asyncio",
                    "department_id": 5
                }
            ]
        }
    }


class SkillUpdate(BaseModel):
    """Схема для частичного обновления скилла. Все поля НЕОБЯЗАТЕЛЬНЫ."""
    name: str | None = Field(
        None,
        min_length=2,
        max_length=100,
        description="Новое название навыка (если меняется)"
    )
    department_id: int | None = Field(
        None,
        gt=0,
        description="Новый ID подразделения (если меняется)"
    )

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