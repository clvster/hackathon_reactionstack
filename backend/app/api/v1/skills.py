from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.direction import Direction
from app.models.skill import PlanItem, Skill
from app.models.user import User
from app.schemas.direction import DirectionCreate, DirectionRead, DirectionUpdate
from app.schemas.skill import (
    PlanItemCreate,
    PlanItemRead,
    PlanItemUpdate,
    SkillCreate,
    SkillRead,
    SkillStatusEnum,
    SkillUpdate,
)
from app.services.access import require_admin, require_manage_user, require_view_user

router = APIRouter(tags=["Справочник скиллов и годовой план"])


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    require_admin(current_user)
    return current_user


async def get_direction_or_404(db: AsyncSession, direction_id: int) -> Direction:
    direction = await db.get(Direction, direction_id)
    if direction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Направление не найдено")
    return direction


async def get_skill_or_404(db: AsyncSession, skill_id: int) -> Skill:
    skill = await db.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Скилл не найден")
    return skill


async def load_plan_items(db: AsyncSession, *conditions) -> list[PlanItem]:
    result = await db.execute(
        select(PlanItem)
        .options(selectinload(PlanItem.skill))
        .where(*conditions)
        .order_by(PlanItem.target_date, PlanItem.id)
        .execution_options(populate_existing=True)
    )
    return list(result.scalars().all())


@router.get("/directions", response_model=List[DirectionRead], summary="Список направлений")
async def list_directions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Direction).order_by(Direction.id))
    return result.scalars().all()


@router.post(
    "/directions",
    response_model=DirectionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать направление (админ)",
)
async def create_direction(
    direction_in: DirectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    direction = Direction(name=direction_in.name.strip())
    db.add(direction)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Такое направление уже есть")
    await db.refresh(direction)
    return direction


@router.patch("/directions/{direction_id}", response_model=DirectionRead, summary="Переименовать направление (админ)")
async def update_direction(
    direction_id: int,
    direction_in: DirectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    direction = await get_direction_or_404(db, direction_id)
    direction.name = direction_in.name.strip()
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Такое направление уже есть")
    await db.refresh(direction)
    return direction


@router.delete(
    "/directions/{direction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить направление (админ)",
)
async def delete_direction(
    direction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    direction = await get_direction_or_404(db, direction_id)
    skills_count = await db.scalar(select(func.count(Skill.id)).where(Skill.direction_id == direction_id))
    if skills_count:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Нельзя удалить направление, пока в нём есть скиллы",
        )
    await db.delete(direction)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/skills", response_model=List[SkillRead], summary="Справочник скиллов")
async def list_skills(
    direction_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Skill).order_by(Skill.direction_id, Skill.name)
    if direction_id is not None:
        query = query.where(Skill.direction_id == direction_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post(
    "/skills",
    response_model=SkillRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить скилл в справочник (админ)",
)
async def create_skill(
    skill_in: SkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    await get_direction_or_404(db, skill_in.direction_id)
    skill = Skill(name=skill_in.name.strip(), direction_id=skill_in.direction_id)
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.patch("/skills/{skill_id}", response_model=SkillRead, summary="Изменить скилл (админ)")
async def update_skill(
    skill_id: int,
    skill_in: SkillUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    skill = await get_skill_or_404(db, skill_id)
    fields = skill_in.model_fields_set
    if "name" in fields and skill_in.name:
        skill.name = skill_in.name.strip()
    if "direction_id" in fields and skill_in.direction_id:
        await get_direction_or_404(db, skill_in.direction_id)
        skill.direction_id = skill_in.direction_id
    await db.commit()
    await db.refresh(skill)
    return skill


@router.delete(
    "/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить скилл (админ)",
)
async def delete_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    skill = await get_skill_or_404(db, skill_id)
    await db.delete(skill)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/users/{user_id}/plan", response_model=List[PlanItemRead], summary="Годовой план сотрудника")
async def get_user_plan(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_view_user(db, current_user, user_id)
    return await load_plan_items(db, PlanItem.user_id == user_id)


@router.post(
    "/users/{user_id}/plan",
    response_model=List[PlanItemRead],
    status_code=status.HTTP_201_CREATED,
    summary="Добавить скиллы в годовой план сотрудника",
)
async def add_skills_to_plan(
    user_id: int,
    plan_items_in: List[PlanItemCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_manage_user(db, current_user, user_id)
    if not plan_items_in:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Список скиллов пуст")

    skill_ids = [item.skill_id for item in plan_items_in]
    if len(skill_ids) != len(set(skill_ids)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Скилл указан в запросе несколько раз")

    found = await db.scalars(select(Skill.id).where(Skill.id.in_(skill_ids)))
    missing = set(skill_ids) - set(found.all())
    if missing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Скиллы не найдены: {sorted(missing)}")

    existing = await db.execute(
        select(Skill.name)
        .join(PlanItem, PlanItem.skill_id == Skill.id)
        .where(PlanItem.user_id == user_id, PlanItem.skill_id.in_(skill_ids))
    )
    existing_names = list(existing.scalars().all())
    if existing_names:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Уже есть в плане: {', '.join(existing_names)}",
        )

    items = [
        PlanItem(user_id=user_id, skill_id=item.skill_id, target_date=item.target_date, status=SkillStatusEnum.PLANNED)
        for item in plan_items_in
    ]
    db.add_all(items)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Скилл уже есть в плане")

    return await load_plan_items(db, PlanItem.id.in_([item.id for item in items]))


@router.patch(
    "/users/{user_id}/plan/{plan_item_id}",
    response_model=PlanItemRead,
    summary="Изменить пункт плана (дату, статус, проблему)",
)
async def update_plan_item(
    user_id: int,
    plan_item_id: int,
    item_in: PlanItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_manage_user(db, current_user, user_id)
    item = await db.get(PlanItem, plan_item_id)
    if item is None or item.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пункт плана не найден")

    fields = item_in.model_fields_set
    if "target_date" in fields and item_in.target_date:
        item.target_date = item_in.target_date
    if "status" in fields and item_in.status:
        item.status = item_in.status
        if item_in.status == SkillStatusEnum.COMPLETED:
            if item.confirmed_at is None:
                item.confirmed_at = date.today()
            item.problem_comment = None
        else:
            item.confirmed_at = None
    if "problem_comment" in fields:
        item.problem_comment = item_in.problem_comment

    await db.commit()
    return (await load_plan_items(db, PlanItem.id == plan_item_id))[0]


@router.delete(
    "/users/{user_id}/plan/{plan_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пункт плана",
)
async def delete_plan_item(
    user_id: int,
    plan_item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_manage_user(db, current_user, user_id)
    item = await db.get(PlanItem, plan_item_id)
    if item is None or item.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пункт плана не найден")
    await db.delete(item)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get(
    "/users/{user_id}/plan",
    response_model=List[PlanItemRead],
    summary="Получить годовой план развития сотрудника"
)
async def get_user_plan(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = select(PlanItem).where(PlanItem.user_id == user_id)
    result = await db.execute(query)
    items = result.scalars().all()

    for item in items:
        await db.refresh(item, attribute_names=["skill"])

    return items
