import asyncio

from sqlalchemy import text

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.department import Department
from app.models.user import User


async def seed_data():
    async with AsyncSessionLocal() as session:
        # Полностью очищаем тестовые данные.
        # CASCADE учитывает внешние ключи между users и departments.
        await session.execute(
            text(
                "TRUNCATE TABLE users, departments "
                "RESTART IDENTITY CASCADE"
            )
        )
        await session.flush()

        # 1. Создаем подразделения
        dep_head = Department(
            name="СТО"
        )
        session.add(dep_head)
        await session.flush()

        dep_engineering = Department(
            name="Head of Engineering",
            parent_id=dep_head.id,
        )
        session.add(dep_engineering)
        await session.flush()

        dep_backend = Department(
            name="Backend Team",
            parent_id=dep_engineering.id,
        )
        session.add(dep_backend)
        await session.flush()

        dep_python = Department(
            name="Python Team",
            parent_id=dep_backend.id,
        )
        session.add(dep_python)
        await session.flush()

        # 2. Создаем пользователей
        admin = User(
            email="admin@test.com",
            hashed_password=get_password_hash("pass123"),
            full_name="Администратор Системы",
            direction="BACK",
            is_admin=True,
            department_id=None,
        )

        cto = User(
            email="cto@test.com",
            hashed_password=get_password_hash("pass123"),
            full_name="Сергей CTO",
            direction="BACK",
            is_admin=False,
            department_id=dep_head.id,
        )

        head_engineering = User(
            email="head@test.com",
            hashed_password=get_password_hash("pass123"),
            full_name="Иван Head of Engineering",
            direction="BACK",
            is_admin=False,
            department_id=dep_engineering.id,
        )

        team_lead = User(
            email="lead@test.com",
            hashed_password=get_password_hash("pass123"),
            full_name="Пётр Backend Team Lead",
            direction="BACK",
            is_admin=False,
            department_id=dep_backend.id,
        )

        junior = User(
            email="junior@test.com",
            hashed_password=get_password_hash("pass123"),
            full_name="Алексей Junior Developer",
            direction="BACK",
            is_admin=False,
            department_id=dep_python.id,
        )

        session.add_all(
            [
                admin,
                cto,
                head_engineering,
                team_lead,
                junior,
            ]
        )

        await session.flush()

        # 3. Назначаем руководителей подразделений
        dep_head.leader_id = cto.id
        dep_engineering.leader_id = head_engineering.id
        dep_backend.leader_id = team_lead.id

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_data())