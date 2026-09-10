import asyncio
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.department import Department
from app.models.user import User

async def seed_data():
    async with AsyncSessionLocal() as session:
        # 1. Создаем подразделения (3 уровня вложенности)
        dep_head = Department(name="Департамент разработки")
        session.add(dep_head)
        await session.flush()

        dep_backend = Department(name="Отдел Backend-разработки", parent_id=dep_head.id)
        session.add(dep_backend)
        await session.flush()

        dep_team = Department(name="Команда Python", parent_id=dep_backend.id)
        session.add(dep_team)
        await session.flush()

        # 2. Создаем пользователей
        admin = User(
            email="admin@test.com",
            hashed_password=get_password_hash("pass123"),
            full_name="Администратор Системы",
            direction="BACK",
            is_admin=True,
            department_id=None
        )
        lead = User(
            email="lead@test.com",
            hashed_password=get_password_hash("pass123"),
            full_name="Иван Руководителев",
            direction="BACK",
            is_admin=False,
            department_id=dep_backend.id
        )
        dev = User(
            email="dev@test.com",
            hashed_password=get_password_hash("pass123"),
            full_name="Пётр Разработчиков",
            direction="BACK",
            is_admin=False,
            department_id=dep_team.id
        )
        session.add_all([admin, lead, dev])
        await session.flush()

        # 3. Назначаем руководителя отделу
        dep_backend.leader_id = lead.id
        await session.commit()
        print("База успешно заполнена начальными данными!")

if __name__ == "__main__":
    asyncio.run(seed_data())