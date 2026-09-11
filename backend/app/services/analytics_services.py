from datetime import date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.skill import PlanItem, Skill
from app.models.user import User
from app.schemas.skill import SkillStatusEnum
from app.schemas.analytics import UserAnalyticsRead, DepartmentAnalyticsRead, MonthlyHistoryItem


class AnalyticsService:

    @staticmethod
    async def get_user_metrics(db: AsyncSession, user_id: int) -> UserAnalyticsRead:
        today = date.today()

        overdue_query = select(func.count(PlanItem.id)).where(
            PlanItem.user_id == user_id,
            PlanItem.status.in_([SkillStatusEnum.PLANNED, SkillStatusEnum.TRAINING]),
            PlanItem.target_date < today
        )
        overdue_res = await db.execute(overdue_query)
        overdue_count = overdue_res.scalar_one()

        dynamics_query = select(
            func.to_char(PlanItem.confirmed_at, "YYYY-MM").label("month_str"),
            func.count(PlanItem.id).label("skill_count")
        ).where(
            PlanItem.user_id == user_id,
            PlanItem.status == SkillStatusEnum.COMPLETED,
            PlanItem.confirmed_at.isnot(None)
        ).group_by("month_str").order_by("month_str")

        dynamics_res = await db.execute(dynamics_query)

        monthly_dynamics = [
            MonthlyHistoryItem(month=row.month_str, count=row.skill_count)
            for row in dynamics_res.fetchall()
        ]

        return UserAnalyticsRead(
            user_id=user_id,
            overdue_skills_count=overdue_count,
            monthly_dynamics=monthly_dynamics
        )

    @staticmethod
    async def get_department_metrics(db: AsyncSession, department_id: int) -> DepartmentAnalyticsRead:
        users_query = select(User.id).where(User.department_id == department_id)
        users_res = await db.execute(users_query)
        user_ids = users_res.scalars().all()

        if not user_ids:
            return DepartmentAnalyticsRead(
                department_id=department_id,
                completion_rate=0.0,
                open_problems_count=0,
                total_planned_skills=0
            )

        metrics_query = select(
            func.count(PlanItem.id).label("total"),
            func.sum(func.cast(PlanItem.status == SkillStatusEnum.COMPLETED, func.Integer)).label("completed"),
            func.sum(func.cast(PlanItem.status == SkillStatusEnum.PROBLEM, func.Integer)).label("problems")
        ).where(PlanItem.user_id.in_(user_ids))

        metrics_res = await db.execute(metrics_query)
        metrics = metrics_res.fetchone()

        total = metrics.total or 0
        completed = metrics.completed or 0
        problems = metrics.problems or 0

        completion_rate = (completed / total * 100.0) if total > 0 else 0.0

        return DepartmentAnalyticsRead(
            department_id=department_id,
            completion_rate=round(completion_rate, 2),
            open_problems_count=problems,
            total_planned_skills=total
        )
