from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем схемы валидации
from app.schemas.skill import SkillCreate, SkillUpdate, SkillRead, PlanItemCreate, PlanItemRead

# СТРОГО ПО СТРУКТУРЕ: Импортируем общие зависимости из файла deps.py УДАЛИТЬ ЭТОТ КОММЕНТАРИЙ!!!!!!!!!!
# Когда первый бэкендер допишет get_db и функции авторизации, они автоматически заработают здесь УДАЛИТЬ ЭТОТ КОММЕНТ!!
from app.api.deps import get_db

router = APIRouter(tags=["Справочник скиллов и Планы развития"])


# --- Имитация проверки ролей через deps.py ---
async def check_admin_or_lead_role():
    """
    Заглушка авторизации. На защите проекта ты покажешь, что код готов
    к интеграции с функциями auth и verify_tree из app/api/deps.py.
    """
    return True


# --- Эндпоинты Справочника Скиллов ---

@router.post(
    "/skills",
    response_model=SkillRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый навык компании"
)
async def create_skill(
        skill_in: SkillCreate,
        db: AsyncSession = Depends(get_db),
        is_authorized: bool = Depends(check_admin_or_lead_role)
):
    """
    Добавление нового навыка в общий справочник.
    Доступно только Администратору или Руководителю.
    """
    # Имитируем сохранение в базу данных с использованием сессии db
    return SkillRead(id=1, name=skill_in.name, department_id=skill_in.department_id)


@router.get(
    "/skills",
    response_model=List[SkillRead],
    summary="Получить список всех навыков компании"
)
async def get_skills(
        department_id: Optional[int] = None,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение списка навыков. Доступно всем авторизованным пользователям.
    Можно отфильтровать навыки по конкретному `department_id` (отделу) из дерева подразделений.
    """
    return [
        SkillRead(id=1, name="Python & FastAPI", department_id=department_id or 5),
        SkillRead(id=2, name="Docker & CI/CD", department_id=department_id or 5),
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
        is_authorized: bool = Depends(check_admin_or_lead_role)
):
    """
    Редактирование параметров навыка.
    Доступно **только Администратору или Руководителю**.
    """
    return SkillRead(
        id=skill_id,
        name=skill_in.name or "Обновленный навык",
        department_id=skill_in.department_id or 5
    )


# --- Эндпоинты Годового плана развития сотрудников ---

@router.post(
    "/users/{user_id}/plan",
    response_model=List[PlanItemRead],
    status_code=status.HTTP_201_CREATED,
    summary="Добавить навыки в годовой план развития сотрудника"
)
async def add_skills_to_plan(
        user_id: int,
        plan_items_in: List[PlanItemCreate],
        db: AsyncSession = Depends(get_db)
):
    """
    Привязка выбранных скиллов к конкретному сотруднику с установкой плановых дат.
    Вызывать этот эндпоинт может сам сотрудник или его руководитель.
    """
    from datetime import date
    from app.schemas.skill import SkillStatusEnum

    mock_response = []
    for index, item in enumerate(plan_items_in):
        mock_response.append(
            PlanItemRead(
                id=100 + index,
                skill=SkillRead(id=item.skill_id, name=f"Тестовый скилл {item.skill_id}", department_id=5),
                target_date=item.target_date,
                status=SkillStatusEnum.PLANNED,
                confirmed_at=None,
                problem_comment=None
            )
        )
    return mock_response
