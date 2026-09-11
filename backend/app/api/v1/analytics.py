from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.analytics import UserAnalyticsRead, DepartmentAnalyticsRead, MonthlyHistoryItem
from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter(tags=["Аналитика и Метрики эффективности"])


@router.get(
    "/analytics/user/{user_id}",
    response_model=UserAnalyticsRead,
    summary="Получить аналитику и динамику развития сотрудника"
)
async def get_user_analytics(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    mock_dynamics = [
        MonthlyHistoryItem(month="2026-06", count=1),
        MonthlyHistoryItem(month="2026-07", count=3),
        MonthlyHistoryItem(month="2026-08", count=2),
    ]

    return UserAnalyticsRead(
        user_id=user_id,
        overdue_skills_count=1,
        monthly_dynamics=mock_dynamics
    )


@router.get(
    "/analytics/department/{department_id}",
    response_model=DepartmentAnalyticsRead,
    summary="Получить сводные метрики по подразделению"
)
async def get_department_analytics(
        department_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return DepartmentAnalyticsRead(
        department_id=department_id,
        completion_rate=68.5,
        open_problems_count=3,
        total_planned_skills=24
    )
