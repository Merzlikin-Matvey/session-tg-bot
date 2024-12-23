import asyncio
from datetime import datetime

from aiogram import Bot

from src.database.db_adapter import DatabaseAdapter
from src.send_task import send_tasks_for_all_users


async def schedule_exams(bot: Bot):
    adapter = DatabaseAdapter()
    exams = adapter.get_all_exams()
    for exam in exams:
        exam_time = exam.timestamp
        if not exam.started and exam_time <= datetime.now():
            await send_tasks_for_all_users(bot, exam)
            exam.started = True
            adapter.db.commit()
    adapter.close()


async def check_new_exams(bot: Bot):
    while True:
        await schedule_exams(bot)
        await asyncio.sleep(1)
