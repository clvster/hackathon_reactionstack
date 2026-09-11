from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.analytics import UserAnalyticsRead, DepartmentAnalyticsRead
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.analytics_services import AnalyticsService

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
    return await AnalyticsService.get_user_metrics(db, user_id)


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
    return await AnalyticsService.get_department_metrics(db, department_id)
