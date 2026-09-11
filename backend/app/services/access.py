from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.user import User
from app.services.tree_services import get_visible_department_ids, user_has_tree_access


async def can_view_user(db: AsyncSession, current_user: User, target_user_id: int) -> bool:
    if current_user.is_admin or current_user.id == target_user_id:
        return True
    return await user_has_tree_access(
        db=db,
        current_user_id=current_user.id,
        target_user_id=target_user_id,
    )


async def can_manage_user(db: AsyncSession, current_user: User, target_user_id: int) -> bool:
    if current_user.is_admin:
        return True
    if current_user.id == target_user_id:
        return False
    return await user_has_tree_access(
        db=db,
        current_user_id=current_user.id,
        target_user_id=target_user_id,
    )


async def ensure_user_exists(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сотрудник не найден")
    return user


async def require_view_user(db: AsyncSession, current_user: User, target_user_id: int) -> None:
    await ensure_user_exists(db, target_user_id)
    if not await can_view_user(db, current_user, target_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому сотруднику")


async def require_manage_user(db: AsyncSession, current_user: User, target_user_id: int) -> None:
    await ensure_user_exists(db, target_user_id)
    if not await can_manage_user(db, current_user, target_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вести план и встречи может только руководитель сотрудника или администратор",
        )


async def require_view_department(db: AsyncSession, current_user: User, department_id: int) -> Department:
    department = await db.get(Department, department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Подразделение не найдено")
    if current_user.is_admin:
        return department
    visible = await get_visible_department_ids(db=db, current_user_id=current_user.id, is_admin=False)
    if department_id not in visible:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому подразделению")
    return department


def require_admin(current_user: User) -> None:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуются права администратора")
