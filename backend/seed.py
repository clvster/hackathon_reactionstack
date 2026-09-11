import asyncio
import random
from datetime import date, datetime, time, timedelta

from sqlalchemy import delete, select, text

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.department import Department
from app.models.direction import Direction
from app.models.meeting import Meeting, MeetingAssessment
from app.models.skill import PlanItem, Skill
from app.models.user import User
from app.schemas.skill import SkillStatusEnum

PASSWORD = "pass123"

DEPARTMENTS = [
    ("cto", "Технический департамент", None),
    ("engineering", "Разработка", "cto"),
    ("backend", "Backend Team", "engineering"),
    ("python", "Python Team", "backend"),
    ("frontend", "Frontend Team", "engineering"),
    ("qa", "QA Team", "cto"),
]

USERS = [
    ("admin", "Администратор Системы", "BACK", None, None, True),
    ("cto", "Сергей Орлов", "BACK", "cto", "cto", False),
    ("head", "Иван Смирнов", "BACK", "engineering", "engineering", False),
    ("lead", "Пётр Кузнецов", "BACK", "backend", "backend", False),
    ("back1", "Анна Волкова", "BACK", "backend", None, False),
    ("back2", "Дмитрий Павлов", "BACK", "backend", None, False),
    ("pylead", "Ольга Морозова", "BACK", "python", "python", False),
    ("junior", "Алексей Новиков", "BACK", "python", None, False),
    ("py1", "Кирилл Фёдоров", "BACK", "python", None, False),
    ("flead", "Мария Соколова", "FRONT", "frontend", "frontend", False),
    ("front1", "Егор Лебедев", "FRONT", "frontend", None, False),
    ("front2", "Полина Зайцева", "FRONT", "frontend", None, False),
    ("front3", "Никита Попов", "FRONT", "frontend", None, False),
    ("qalead", "Елена Васильева", "QA", "qa", "qa", False),
    ("qa1", "Артём Михайлов", "QA", "qa", None, False),
    ("qa2", "Софья Козлова", "QA", "qa", None, False),
]

SKILLS = {
    "BACK": ["Python и asyncio", "FastAPI", "PostgreSQL и SQL", "Docker и CI/CD", "Тестирование с pytest", "Архитектура сервисов"],
    "FRONT": ["TypeScript", "React", "Управление состоянием", "Вёрстка и доступность", "Тестирование фронтенда", "Производительность веба"],
    "QA": ["Тест-дизайн", "Автотесты Playwright", "API-тестирование", "Нагрузочное тестирование", "Баг-репорты и процессы", "SQL для тестировщика"],
}

SUMMARIES = [
    "## Итоги встречи\n\n- Разобрали прогресс по плану развития\n- {done}\n- Договорились о следующих шагах до следующей встречи\n\n**Следующая встреча:** через месяц",
    "## Ретроспектива месяца\n\n1. Что получилось: {done}\n2. Что мешает: нехватка времени на обучение\n3. Действия: выделить 2 часа в неделю на практику",
    "## 1:1\n\nОбсудили задачи в спринте и развитие.\n\n- {done}\n- Порекомендовал материалы и внутренний курс\n\n> Сотрудник доволен темпом, нагрузка нормальная",
]

LINKS = [
    "https://gitlab.example.com/reactionstack/app/-/merge_requests/{n}",
    "https://docs.example.com/growth/plan-{n}",
    "https://wiki.example.com/pr/meeting-{n}",
]

PROBLEMS = [
    "Не хватает практики на реальных задачах",
    "Теория есть, но не применяется в проекте",
    "Затянул сроки из-за нагрузки в спринте",
    "Нужна помощь ментора, самостоятельно не продвигается",
]


async def ensure_directions(session) -> dict[str, int]:
    await session.execute(delete(Direction).where(Direction.name.notin_(list(SKILLS))))
    result = await session.execute(select(Direction))
    directions = {d.name: d.id for d in result.scalars().all()}
    for name in SKILLS:
        if name not in directions:
            direction = Direction(name=name)
            session.add(direction)
            await session.flush()
            directions[name] = direction.id
    return directions


def manager_of(user_key: str, users: dict, departments: dict, dept_leaders: dict, dept_parent: dict):
    _, _, _, dept_key, leads, _ = next(u for u in USERS if u[0] == user_key)
    if dept_key is None:
        return None
    leader = dept_leaders.get(dept_key)
    if leader and leader != user_key:
        return users[leader]
    parent = dept_parent.get(dept_key)
    while parent is not None:
        leader = dept_leaders.get(parent)
        if leader:
            return users[leader]
        parent = dept_parent.get(parent)
    return users["admin"]


async def seed_data():
    rng = random.Random(42)
    today = date.today()
    password_hash = get_password_hash(PASSWORD)

    async with AsyncSessionLocal() as session:
        await session.execute(
            text(
                "TRUNCATE TABLE meeting_assessments, meetings, plan_items, skills, users, departments "
                "RESTART IDENTITY CASCADE"
            )
        )
        directions = await ensure_directions(session)

        departments: dict[str, Department] = {}
        dept_parent: dict[str, str | None] = {}
        for key, name, parent_key in DEPARTMENTS:
            department = Department(name=name, parent_id=departments[parent_key].id if parent_key else None)
            session.add(department)
            await session.flush()
            departments[key] = department
            dept_parent[key] = parent_key

        users: dict[str, User] = {}
        dept_leaders: dict[str, str] = {}
        for username, full_name, direction, dept_key, leads, is_admin in USERS:
            user = User(
                username=username,
                email=f"{username}@reactionstack.dev",
                hashed_password=password_hash,
                full_name=full_name,
                direction=direction,
                is_admin=is_admin,
                department_id=departments[dept_key].id if dept_key else None,
            )
            session.add(user)
            users[username] = user
            if leads:
                dept_leaders[leads] = username
        await session.flush()

        for dept_key, username in dept_leaders.items():
            departments[dept_key].leader_id = users[username].id

        skills: dict[str, list[Skill]] = {}
        for direction_name, names in SKILLS.items():
            skills[direction_name] = []
            for name in names:
                skill = Skill(name=name, direction_id=directions[direction_name])
                session.add(skill)
                skills[direction_name].append(skill)
        await session.flush()

        meetings_count = 0
        link_counter = 100
        for username, _, direction, dept_key, _, is_admin in USERS:
            if is_admin:
                continue
            user = users[username]
            manager = manager_of(username, users, departments, dept_leaders, dept_parent)
            user_skills = rng.sample(skills[direction], k=rng.randint(4, 5))

            meeting_days = sorted(
                today - timedelta(days=offset)
                for offset in rng.sample([150, 125, 100, 75, 50, 30, 12], k=rng.randint(3, 4))
            )
            outcomes: dict[date, list[tuple[Skill, str]]] = {day: [] for day in meeting_days}

            plan_items: list[PlanItem] = []
            for index, skill in enumerate(user_skills):
                roll = rng.random()
                if index < 2 or roll < 0.35:
                    day = rng.choice(meeting_days)
                    target = day + timedelta(days=rng.randint(0, 25))
                    item = PlanItem(user_id=user.id, skill_id=skill.id, target_date=target,
                                    status=SkillStatusEnum.COMPLETED, confirmed_at=day)
                    outcomes[day].append((skill, "done"))
                elif roll < 0.55:
                    day = rng.choice(meeting_days[1:] or meeting_days)
                    comment = rng.choice(PROBLEMS)
                    target = today + timedelta(days=rng.randint(-40, 30))
                    item = PlanItem(user_id=user.id, skill_id=skill.id, target_date=target,
                                    status=SkillStatusEnum.PROBLEM, problem_comment=comment)
                    outcomes[day].append((skill, "problem:" + comment))
                elif roll < 0.75:
                    target = today - timedelta(days=rng.randint(5, 45))
                    item = PlanItem(user_id=user.id, skill_id=skill.id, target_date=target,
                                    status=SkillStatusEnum.TRAINING)
                    outcomes[meeting_days[-1]].append((skill, "discuss"))
                else:
                    target = today + timedelta(days=rng.randint(20, 110))
                    item = PlanItem(user_id=user.id, skill_id=skill.id, target_date=target,
                                    status=rng.choice([SkillStatusEnum.PLANNED, SkillStatusEnum.TRAINING]))
                plan_items.append(item)
            session.add_all(plan_items)

            if manager is None:
                continue
            for day in meeting_days:
                done_names = [s.name for s, o in outcomes[day] if o == "done"]
                done_text = f"Подтверждены скиллы: {', '.join(done_names)}" if done_names else "Скиллы в работе, подтверждений пока нет"
                link_counter += 1
                has_global_problem = rng.random() < 0.15
                meeting = Meeting(
                    interviewer_id=manager.id,
                    participant_id=user.id,
                    meeting_date=datetime.combine(day, time(hour=rng.choice([10, 11, 14, 16]))),
                    summary_markdown=rng.choice(SUMMARIES).format(done=done_text),
                    files_and_links=[rng.choice(LINKS).format(n=link_counter)],
                    problem_comment="Снизилась вовлечённость, обсудить нагрузку" if has_global_problem else None,
                    assessments=[],
                )
                for skill, outcome in outcomes[day]:
                    meeting.assessments.append(
                        MeetingAssessment(
                            skill_id=skill.id,
                            is_completed=outcome == "done",
                            has_problem=outcome.startswith("problem:"),
                            comment=outcome.split(":", 1)[1] if outcome.startswith("problem:") else None,
                        )
                    )
                session.add(meeting)
                meetings_count += 1

        await session.commit()

        print(f"Подразделений: {len(departments)}, сотрудников: {len(users)}, "
              f"скиллов: {sum(len(v) for v in skills.values())}, встреч: {meetings_count}")
        print(f"Логины (пароль у всех {PASSWORD}): " + ", ".join(u[0] for u in USERS))


if __name__ == "__main__":
    asyncio.run(seed_data())
