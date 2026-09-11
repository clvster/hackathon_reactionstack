from collections import Counter
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.department import Department
from app.models.skill import PlanItem
from app.models.user import User
from app.schemas.analytics import (
    DepartmentAnalyticsRead,
    EmployeeProgressItem,
    MonthlyHistoryItem,
    OverdueSkillItem,
    UserAnalyticsRead,
)
from app.schemas.skill import SkillStatusEnum
from app.services.tree_services import get_department_subtree_ids


def is_overdue(item: PlanItem, today: date) -> bool:
    return item.status != SkillStatusEnum.COMPLETED and item.target_date < today


def summarize(items: list[PlanItem], today: date) -> dict:
    total = len(items)
    completed = sum(1 for i in items if i.status == SkillStatusEnum.COMPLETED)
    problems = sum(1 for i in items if i.status == SkillStatusEnum.PROBLEM)
    overdue = sum(1 for i in items if is_overdue(i, today))
    rate = round(completed / total * 100, 1) if total else 0.0
    return {
        "total_planned_skills": total,
        "completed_skills": completed,
        "open_problems_count": problems,
        "overdue_skills_count": overdue,
        "completion_rate": rate,
    }


def monthly_dynamics(items: list[PlanItem]) -> list[MonthlyHistoryItem]:
    counter = Counter(
        i.confirmed_at.strftime("%Y-%m")
        for i in items
        if i.status == SkillStatusEnum.COMPLETED and i.confirmed_at is not None
    )
    return [MonthlyHistoryItem(month=month, count=count) for month, count in sorted(counter.items())]


class AnalyticsService:
    @staticmethod
    async def get_user_metrics(db: AsyncSession, user_id: int) -> UserAnalyticsRead:
        today = date.today()
        user = await db.get(User, user_id)
        result = await db.execute(
            select(PlanItem).options(selectinload(PlanItem.skill)).where(PlanItem.user_id == user_id)
        )
        items = list(result.scalars().all())
        overdue = sorted((i for i in items if is_overdue(i, today)), key=lambda i: i.target_date)
        return UserAnalyticsRead(
            user_id=user_id,
            full_name=user.full_name,
            monthly_dynamics=monthly_dynamics(items),
            overdue_skills=[
                OverdueSkillItem(
                    plan_item_id=i.id,
                    skill_id=i.skill_id,
                    skill_name=i.skill.name,
                    target_date=i.target_date,
                    days_overdue=(today - i.target_date).days,
                )
                for i in overdue
            ],
            **summarize(items, today),
        )

    @staticmethod
    async def get_department_metrics(db: AsyncSession, department: Department) -> DepartmentAnalyticsRead:
        today = date.today()
        department_ids = await get_department_subtree_ids(db, department.id)
        users_result = await db.execute(
            select(User).where(User.department_id.in_(department_ids)).order_by(User.full_name)
        )
        users = list(users_result.scalars().all())
        user_ids = [u.id for u in users]

        items: list[PlanItem] = []
        if user_ids:
            items_result = await db.execute(select(PlanItem).where(PlanItem.user_id.in_(user_ids)))
            items = list(items_result.scalars().all())

        by_user: dict[int, list[PlanItem]] = {uid: [] for uid in user_ids}
        for item in items:
            by_user[item.user_id].append(item)

        employees = [
            EmployeeProgressItem(
                user_id=u.id,
                full_name=u.full_name,
                direction=u.direction,
                department_id=u.department_id,
                **summarize(by_user[u.id], today),
            )
            for u in users
        ]

        return DepartmentAnalyticsRead(
            department_id=department.id,
            department_name=department.name,
            employees_count=len(users),
            monthly_dynamics=monthly_dynamics(items),
            employees=employees,
            **summarize(items, today),
        )
