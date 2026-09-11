from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional

from app.api.deps import get_current_user, verify_tree_access
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.department import Department
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
)
from app.services.tree_services import get_visible_user_ids


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверяет, является ли текущий пользователь администратором.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )

    return current_user


@router.get(
    "",
    response_model=list[UserResponse],
)
async def get_users(
    direction: Optional[str] = None,
    department_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Список пользователей с фильтрацией по направлению и подразделению.

    Доступ:
    - администратор -> все пользователи;
    - руководитель -> он сам + вся его ветка подчинённых;
    - сотрудник без подчинённых -> только он сам.
    """

    visible_ids = await get_visible_user_ids(
        db=db,
        current_user_id=current_user.id,
        is_admin=current_user.is_admin,
    )

    query = select(User).where(User.id.in_(visible_ids)).order_by(User.id)

    if direction is not None:
        query = query.where(User.direction == direction)

    if department_id is not None:
        query = query.where(User.department_id == department_id)

    result = await db.execute(query)

    return result.scalars().all()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(verify_tree_access),
):
    """
    Получить конкретного пользователя.

    Доступ:
    - admin -> любой;
    - пользователь -> сам себя;
    - руководитель -> свою ветку.
    """

    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Создать нового пользователя.
    """

    # Проверяем уникальность username.
    result = await db.execute(
        select(User).where(User.username == data.username)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким username уже существует",
        )

    # Проверяем уникальность email, если он указан.
    if data.email is not None:
        result = await db.execute(
            select(User).where(User.email == data.email)
        )

        existing_email_user = result.scalar_one_or_none()

        if existing_email_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email уже существует",
            )

    # Проверяем подразделение.
    if data.department_id is not None:
        result = await db.execute(
            select(Department).where(
                Department.id == data.department_id
            )
        )

        department = result.scalar_one_or_none()

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подразделение не найдено",
            )

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        direction=data.direction,
        department_id=data.department_id,
        is_admin=data.is_admin,
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    fields = data.model_fields_set

    # Username
    if "username" in fields:
        if data.username is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username не может быть null",
            )

        result = await db.execute(
            select(User).where(
                User.username == data.username,
                User.id != user_id,
            )
        )

        existing_user = result.scalar_one_or_none()

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким username уже существует",
            )

        user.username = data.username

    # Email
    if "email" in fields:
        if data.email is not None:
            result = await db.execute(
                select(User).where(
                    User.email == data.email,
                    User.id != user_id,
                )
            )

            existing_user = result.scalar_one_or_none()

            if existing_user is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким email уже существует",
                )

        user.email = data.email

    # Пароль
    if "password" in fields:
        if data.password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль не может быть null",
            )

        user.hashed_password = get_password_hash(
            data.password
        )

    # ФИО
    if "full_name" in fields:
        if data.full_name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ФИО не может быть null",
            )

        user.full_name = data.full_name

    # Направление
    if "direction" in fields:
        if data.direction is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Направление не может быть null",
            )

        user.direction = data.direction

    # Подразделение
    if "department_id" in fields:
        if data.department_id is None:
            # Явно отвязываем пользователя от подразделения.
            user.department_id = None
        else:
            result = await db.execute(
                select(Department).where(
                    Department.id == data.department_id
                )
            )

            department = result.scalar_one_or_none()

            if department is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Подразделение не найдено",
                )

            user.department_id = data.department_id

    # Администратор
    if "is_admin" in fields:
        if data.is_admin is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="is_admin не может быть null",
            )

        user.is_admin = data.is_admin

    await db.commit()
    await db.refresh(user)

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Удалить пользователя.
    """

    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    # Не позволяем админу случайно удалить самого себя.
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить текущего администратора",
        )

    # Запрещаем удалять пользователя, пока он числится руководителем
    # хотя бы одного подразделения — иначе дерево останется без
    # руководителя молча (leader_id тихо уйдёт в NULL по FK).
    result = await db.execute(
        select(Department).where(Department.leader_id == user_id)
    )
    led_departments = result.scalars().all()

    if led_departments:
        names = ", ".join(dep.name for dep in led_departments)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Нельзя удалить пользователя: он является руководителем "
                f"подразделения(ий): {names}. Сначала назначьте другого "
                "руководителя или снимите его с должности."
            ),
        )

    await db.delete(user)
    await db.commit()