from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.skill import SkillCreate, SkillUpdate, SkillRead, PlanItemCreate, PlanItemRead
from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter(tags=["Справочник скиллов и Направления"])


async def check_admin_or_lead_role(
        current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin and not getattr(current_user, "is_lead", False) and not getattr(current_user,
                                                                                                 "leader_id", None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Действие доступно только Администратору или Руководителю",
        )
    return current_user


@router.post(
    "/skills",
    response_model=SkillRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый навык компании"
)
async def create_skill(
        skill_in: SkillCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(check_admin_or_lead_role)
):
    return SkillRead(id=1, name=skill_in.name, direction_id=skill_in.direction_id)


@router.get(
    "/skills",
    response_model=List[SkillRead],
    summary="Получить список всех навыков компании"
)
async def get_skills(
        direction_id: Optional[int] = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return [
        SkillRead(id=1, name="Python & FastAPI", direction_id=direction_id or 5),
        SkillRead(id=2, name="Docker & CI/CD", direction_id=direction_id or 5),
    ]


@router.patch(
    "/skills/{skill_id}",
    response_model=SkillRead,
    summary="Редактировать существующий навык"
)
async def update_skill(
        skill_id: int,
        skill_in: SkillUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(check_admin_or_lead_role)
):
    return SkillRead(
        id=skill_id,
        name=skill_in.name or "Обновленный навык",
        direction_id=skill_in.direction_id or 5
    )


@router.post(
    "/users/{user_id}/plan",
    response_model=List[PlanItemRead],
    status_code=status.HTTP_201_CREATED,
    summary="Добавить навыки в годовой план развития сотрудника"
)
async def add_skills_to_plan(
        user_id: int,
        plan_items_in: List[PlanItemCreate],
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    from app.schemas.skill import SkillStatusEnum

    mock_response = []
    for index, item in enumerate(plan_items_in):
        mock_response.append(
            PlanItemRead(
                id=100 + index,
                skill=SkillRead(id=item.skill_id, name=f"Тестовый скилл {item.skill_id}", direction_id=5),
                target_date=item.target_date,
                status=SkillStatusEnum.PLANNED,
                confirmed_at=None,
                problem_comment=None
            )
        )
    return mock_response
