from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.user import User


async def get_department_subtree_ids(
    db: AsyncSession,
    department_id: int,
) -> list[int]:
    """
    Возвращает ID подразделения и всех его потомков.
    """

    department_tree = (
        select(Department.id)
        .where(Department.id == department_id)
        .cte(
            name="department_tree",
            recursive=True,
        )
    )

    department_tree = department_tree.union_all(
        select(Department.id).where(
            Department.parent_id == department_tree.c.id
        )
    )

    result = await db.execute(
        select(department_tree.c.id)
    )

    return list(result.scalars().all())


async def get_leader_subtree_ids(
    db: AsyncSession,
    leader_id: int,
) -> list[int]:
    """
    Возвращает ID всех подразделений, которыми руководит пользователь,
    и всех их дочерних подразделений.
    """

    department_tree = (
        select(Department.id)
        .where(Department.leader_id == leader_id)
        .cte(
            name="leader_department_tree",
            recursive=True,
        )
    )

    department_tree = department_tree.union_all(
        select(Department.id).where(
            Department.parent_id == department_tree.c.id
        )
    )

    result = await db.execute(
        select(department_tree.c.id)
    )

    return list(dict.fromkeys(result.scalars().all()))


async def get_department_tree_by_ids(
    db: AsyncSession,
    department_ids: list[int],
) -> list[dict]:
    """
    Получает подразделения по ID и собирает из них вложенное дерево.

    В корни результата попадут только те подразделения,
    у которых родитель отсутствует в переданном списке.
    """

    if not department_ids:
        return []

    result = await db.execute(
        select(Department)
        .where(Department.id.in_(department_ids))
        .order_by(Department.id)
    )

    departments = list(result.scalars().all())

    nodes = {
        department.id: {
            "id": department.id,
            "name": department.name,
            "parent_id": department.parent_id,
            "leader_id": department.leader_id,
            "children": [],
        }
        for department in departments
    }

    roots = []

    for department in departments:
        node = nodes[department.id]

        if (
            department.parent_id is None
            or department.parent_id not in nodes
        ):
            roots.append(node)
        else:
            nodes[department.parent_id]["children"].append(node)

    return roots


async def get_all_departments_tree(
    db: AsyncSession,
) -> list[dict]:
    """
    Возвращает полное дерево компании.
    """

    result = await db.execute(
        select(Department).order_by(Department.id)
    )

    departments = list(result.scalars().all())

    nodes = {
        department.id: {
            "id": department.id,
            "name": department.name,
            "parent_id": department.parent_id,
            "leader_id": department.leader_id,
            "children": [],
        }
        for department in departments
    }

    roots = []

    for department in departments:
        node = nodes[department.id]

        if department.parent_id is None:
            roots.append(node)
        else:
            parent = nodes.get(department.parent_id)

            if parent is not None:
                parent["children"].append(node)

    return roots


async def is_department_descendant(
    db: AsyncSession,
    department_id: int,
    possible_parent_id: int,
) -> bool:
    """
    Проверяет, является ли possible_parent_id
    потомком department_id.
    """

    subtree_ids = await get_department_subtree_ids(
        db,
        department_id,
    )

    return possible_parent_id in subtree_ids


async def user_has_tree_access(
    db: AsyncSession,
    current_user_id: int,
    target_user_id: int,
) -> bool:
    """
    Проверяет доступ current_user к target_user.

    Пользователь имеет доступ:
    - к самому себе;
    - к пользователям в подразделениях,
      которыми он руководит, и всех их потомках.
    """

    if current_user_id == target_user_id:
        return True

    result = await db.execute(
        select(User.department_id).where(
            User.id == target_user_id
        )
    )

    target_department_id = result.scalar_one_or_none()

    if target_department_id is None:
        return False

    department_tree = (
        select(Department.id)
        .where(Department.leader_id == current_user_id)
        .cte(
            name="leader_departments",
            recursive=True,
        )
    )

    department_tree = department_tree.union_all(
        select(Department.id).where(
            Department.parent_id == department_tree.c.id
        )
    )

    result = await db.execute(
        select(
            exists().where(
                department_tree.c.id == target_department_id
            )
        )
    )

    return bool(result.scalar())