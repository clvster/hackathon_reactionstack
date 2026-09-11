from typing import List
from pydantic import BaseModel, Field

class MonthlyHistoryItem(BaseModel):
    month: str = Field(..., description="Год и месяц в формате YYYY-MM", examples=["2026-09"])
    count: int = Field(..., description="Количество успешно подтвержденных навыков в этом месяце", examples=[3])

class UserAnalyticsRead(BaseModel):
    user_id: int = Field(..., description="ID сотрудника")
    overdue_skills_count: int = Field(..., description="Количество скиллов в плане, по которым просрочена плановая дата подтверждения", examples=[2])
    monthly_dynamics: List[MonthlyHistoryItem] = Field(
        default=[],
        description="История подтверждения навыков по месяцам (массив для построения графика)"
    )

class DepartmentAnalyticsRead(BaseModel):
    department_id: int = Field(..., description="ID анализируемого подразделения")
    completion_rate: float = Field(..., description="Процент выполнения планов развития командой (от 0.0 до 100.0)", examples=[72.5])
    open_problems_count: int = Field(..., description="Количество текущих открытых проблем у сотрудников в этом отделе", examples=[5])
    total_planned_skills: int = Field(..., description="Общее количество запланированных скиллов у всех сотрудников подразделения суммарно", examples=[48])
