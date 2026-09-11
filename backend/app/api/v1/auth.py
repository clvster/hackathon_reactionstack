from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Получить всех пользователей.
    Доступно только администратору.
    """
    result = await db.execute(
        select(User).order_by(User.id)
    )
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
    Доступ: admin -> любой; пользователь -> сам себя; руководитель -> свою ветку.
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
    Создать нового пользователя с коротким логином от сисадмина.
    """
    # Изменено под логин
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким логином уже существует",
        )

    # Проверяем подразделение
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

    # Изменено под логин
    user = User(
        username=data.username,
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

    # Изменено под логин
    if "username" in fields:
        if data.username is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Логин не может быть null",
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
                detail="Пользователь с таким логином уже существует",
            )

        user.username = data.username

    # Пароль
    if "password" in fields:
        if data.password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль не может быть null",
            )
        user.hashed_password = get_password_hash(data.password)

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
            user.department_id = None
        else:
            result = await db.execute(
                select(Department).where(Department.id == data.department_id)
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
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить текущего администратора",
        )

    await db.delete(user)
    await db.commit()
