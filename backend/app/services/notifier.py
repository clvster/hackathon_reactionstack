import os
from datetime import date, timedelta

from aiogram import Bot
from app.core.database import get_db
from app.models.skill import PlanItem
from app.models.user import User
from app.schemas.skill import SkillStatusEnum
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

_bot: Bot | None = None


def get_bot() -> Bot | None:
    """Ленивая инициализация бота. Возвращает None, если токен не задан,
    чтобы планировщик не падал и не слал в MOCK_TOKEN."""
    global _bot
    if not TELEGRAM_TOKEN:
        return None
    if _bot is None:
        _bot = Bot(token=TELEGRAM_TOKEN)
    return _bot


async def send_telegram_alert(chat_id: str, text: str) -> None:
    bot = get_bot()
    if bot is None:
        return
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception:
        pass


async def check_deadlines_job() -> None:
    async for db in get_db():
        today = date.today()
        alert_date = today + timedelta(days=3)

        query = select(PlanItem).where(
            PlanItem.status.in_([SkillStatusEnum.PLANNED, SkillStatusEnum.TRAINING]),
            PlanItem.target_date <= alert_date,
        )
        result = await db.execute(query)
        items = result.scalars().all()

        for item in items:
            user = await db.get(User, item.user_id)
            if user and user.tg_chat_id:
                text = (
                    f"Привет, *{user.full_name}*!\n\n"
                    f"Напоминаем, что плановый срок подтверждения твоего навыка "
                    f"подходит к концу: {item.target_date}."
                )
                await send_telegram_alert(user.tg_chat_id, text)
        break


def start_scheduler() -> None:
    if not TELEGRAM_TOKEN:
        # Токен не задан (например, в CI или локально без .env) — не запускаем.
        return
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_deadlines_job, "cron", hour=9, minute=0)
    scheduler.start()
