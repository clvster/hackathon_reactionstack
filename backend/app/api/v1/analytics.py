from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.analytics import DepartmentAnalyticsRead, UserAnalyticsRead
from app.services.access import require_view_department, require_view_user
from app.services.analytics_services import AnalyticsService

router = APIRouter(tags=["Аналитика развития"])


@router.get(
    "/analytics/user/{user_id}",
    response_model=UserAnalyticsRead,
    summary="Аналитика сотрудника: динамика, отставание от плана",
)
async def get_user_analytics(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_view_user(db, current_user, user_id)
    return await AnalyticsService.get_user_metrics(db, user_id)


@router.get(
    "/analytics/department/{department_id}",
    response_model=DepartmentAnalyticsRead,
    summary="Аналитика подразделения с учётом всех дочерних",
)
async def get_department_analytics(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    department = await require_view_department(db, current_user, department_id)
    return await AnalyticsService.get_department_metrics(db, department)
