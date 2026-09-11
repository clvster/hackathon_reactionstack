from datetime import date
from typing import List

from pydantic import BaseModel, Field


class MonthlyHistoryItem(BaseModel):
    month: str = Field(..., examples=["2026-09"])
    count: int = Field(..., examples=[3])


class OverdueSkillItem(BaseModel):
    plan_item_id: int
    skill_id: int
    skill_name: str
    target_date: date
    days_overdue: int


class UserAnalyticsRead(BaseModel):
    user_id: int
    full_name: str
    total_planned_skills: int
    completed_skills: int
    open_problems_count: int
    overdue_skills_count: int
    completion_rate: float
    monthly_dynamics: List[MonthlyHistoryItem] = []
    overdue_skills: List[OverdueSkillItem] = []


class EmployeeProgressItem(BaseModel):
    user_id: int
    full_name: str
    direction: str
    department_id: int | None
    total_planned_skills: int
    completed_skills: int
    open_problems_count: int
    overdue_skills_count: int
    completion_rate: float


class DepartmentAnalyticsRead(BaseModel):
    department_id: int
    department_name: str
    employees_count: int
    total_planned_skills: int
    completed_skills: int
    open_problems_count: int
    overdue_skills_count: int
    completion_rate: float
    monthly_dynamics: List[MonthlyHistoryItem] = []
    employees: List[EmployeeProgressItem] = []
