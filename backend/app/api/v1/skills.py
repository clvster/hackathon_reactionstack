from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.skill import SkillCreate, SkillUpdate, SkillRead, PlanItemCreate, PlanItemRead
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.skill import Skill, PlanItem

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
    db_skill = Skill(name=skill_in.name, direction_id=skill_in.direction_id)
    db.add(db_skill)
    await db.commit()
    await db.refresh(db_skill)
    return db_skill


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
    query = select(Skill)
    if direction_id is not None:
        query = query.where(Skill.direction_id == direction_id)

    result = await db.execute(query)
    return result.scalars().all()


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
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    db_skill = result.scalar_one_or_none()

    if db_skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Навык не найден"
        )

    fields = skill_in.model_fields_set
    if "name" in fields:
        db_skill.name = skill_in.name
    if "direction_id" in fields:
        db_skill.direction_id = skill_in.direction_id

    await db.commit()
    await db.refresh(db_skill)
    return db_skill


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

    created_items = []
    for item in plan_items_in:
        db_plan_item = PlanItem(
            user_id=user_id,
            skill_id=item.skill_id,
            target_date=item.target_date,
            status=SkillStatusEnum.PLANNED
        )
        db.add(db_plan_item)
        created_items.append(db_plan_item)

    await db.commit()

    response_items = []
    for item in created_items:
        await db.refresh(item, attribute_names=["skill"])
        response_items.append(item)

    return response_items
