from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.v1.users import require_admin
from app.core.database import get_db
from app.models.department import Department
from app.models.user import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)
from app.services.access import require_view_department
from app.services.tree_services import (
    get_all_departments_tree,
    get_leader_subtree_ids,
    get_department_tree_by_ids,
    get_visible_department_ids,
    is_department_descendant,
)


router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )

    if data.parent_id is not None:
        result = await db.execute(
            select(Department).where(
                Department.id == data.parent_id
            )
        )

        parent = result.scalar_one_or_none()

        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Родительское подразделение не найдено",
            )

    if data.leader_id is not None:
        result = await db.execute(
            select(User).where(
                User.id == data.leader_id
            )
        )

        leader = result.scalar_one_or_none()

        if leader is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Руководитель не найден",
            )

    department = Department(
        name=data.name,
        parent_id=data.parent_id,
        leader_id=data.leader_id,
    )

    db.add(department)

    await db.commit()
    await db.refresh(department)

    return department


@router.get(
    "",
    response_model=list[DepartmentResponse],
)
async def get_departments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Список подразделений.

    - Администратор -> все подразделения.
    - Руководитель -> подразделения, которыми он руководит, и их поддеревья.
    - Сотрудник без подчинённых -> пустой список.
    """

    visible_ids = await get_visible_department_ids(
        db=db,
        current_user_id=current_user.id,
        is_admin=current_user.is_admin,
    )

    query = select(Department).order_by(Department.id)

    if not current_user.is_admin:
        query = query.where(Department.id.in_(visible_ids))

    result = await db.execute(query)

    return result.scalars().all()


@router.get("/my-tree")
async def get_my_department_tree(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Возвращает дерево, доступное текущему пользователю.

    ADMIN:
        получает всю структуру.

    LEADER:
        получает свои подразделения и всё их поддерево.

    EMPLOYEE:
        получает 403.
    """

    # Администратор видит всю компанию.
    if current_user.is_admin:
        return await get_all_departments_tree(db)

    # Находим подразделения, которыми руководит текущий пользователь.
    department_ids = await get_leader_subtree_ids(
        db=db,
        leader_id=current_user.id,
    )

    # Если пользователь ни одним подразделением не руководит,
    # значит у него нет дерева для просмотра.
    if not department_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У пользователя нет подчинённых",
        )

    return await get_department_tree_by_ids(
        db=db,
        department_ids=department_ids,
    )


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
async def get_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Карточка подразделения.

    Доступ: администратор -> любое; руководитель -> подразделения из
    своей ветки (см. require_view_department).
    """

    return await require_view_department(db, current_user, department_id)


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
)
async def update_department(
    department_id: int,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(
        select(Department).where(
            Department.id == department_id
        )
    )

    department = result.scalar_one_or_none()

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подразделение не найдено",
        )

    fields = data.model_fields_set

    # Название
    if "name" in fields:
        if data.name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Название подразделения не может быть null",
            )

        department.name = data.name

    # Родительское подразделение
    if "parent_id" in fields:
        if data.parent_id is None:
            # Перемещаем подразделение в корень.
            department.parent_id = None

        else:
            # Нельзя сделать себя родителем.
            if data.parent_id == department.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Подразделение не может быть родителем самому себе",
                )

            # Проверяем существование нового родителя.
            result = await db.execute(
                select(Department).where(
                    Department.id == data.parent_id
                )
            )

            parent = result.scalar_one_or_none()

            if parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Родительское подразделение не найдено",
                )

            # Запрещаем перемещение внутрь собственного поддерева.
            is_descendant = await is_department_descendant(
                db=db,
                department_id=department.id,
                possible_parent_id=data.parent_id,
            )

            if is_descendant:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Нельзя переместить подразделение "
                        "внутрь собственного поддерева"
                    ),
                )

            department.parent_id = data.parent_id

    # Руководитель
    if "leader_id" in fields:
        if data.leader_id is None:
            # Убираем руководителя.
            department.leader_id = None

        else:
            result = await db.execute(
                select(User).where(
                    User.id == data.leader_id
                )
            )

            leader = result.scalar_one_or_none()

            if leader is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Руководитель не найден",
                )

            department.leader_id = data.leader_id

    await db.commit()
    await db.refresh(department)

    return department


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )

    result = await db.execute(
        select(Department).where(
            Department.id == department_id
        )
    )

    department = result.scalar_one_or_none()

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подразделение не найдено",
        )

    # "Сшиваем" дерево: дети удаляемого узла переезжают к его родителю,
    # вместо того чтобы молча стать отдельными корневыми деревьями
    # (department.parent_id -> NULL по FK, если этого не сделать явно).
    result = await db.execute(
        select(Department).where(Department.parent_id == department_id)
    )
    children = result.scalars().all()

    for child in children:
        child.parent_id = department.parent_id

    # leader_id самого удаляемого подразделения уходит вместе со строкой —
    # ничего "висячего" не остаётся, т.к. эта информация не хранится
    # больше нигде (в отличие от department_id у User, для которого
    # уже есть ondelete=SET NULL на FK).
    await db.delete(department)
    await db.commit()