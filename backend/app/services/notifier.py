import os
from datetime import date, timedelta
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.skill import PlanItem
from app.models.user import User
from app.schemas.skill import SkillStatusEnum

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "MOCK_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)


async def send_telegram_alert(chat_id: str, text: str):
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception:
        pass


async def check_deadlines_job():
    async for db in get_db():
        today = date.today()
        alert_date = today + timedelta(days=3)

        query = select(PlanItem).where(
            PlanItem.status.in_([SkillStatusEnum.PLANNED, SkillStatusEnum.TRAINING]),
            PlanItem.target_date <= alert_date
        )
        result = await db.execute(query)
        items = result.scalars().all()

        for item in items:
            user_query = select(User).where(User.id == item.user_id)
            user_res = await db.execute(user_query)
            user = user_res.scalar_one_or_none()

            if user and getattr(user, "tg_chat_id", None):
                text = f"Привет, *{user.full_name}*!\n\nНапоминаем, что плановый срок подтверждения твоего навыка подходит к концу: {item.target_date}."
                await send_telegram_alert(user.tg_chat_id, text)
        break


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_deadlines_job, "cron", hour=9, minute=0)
    scheduler.start()
