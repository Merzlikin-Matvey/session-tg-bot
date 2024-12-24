import asyncio
from datetime import datetime

from aiogram import Bot
import yaml

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
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            db_check_interval = int(config['db_check_interval'])
    except Exception as e:
        print("Error while reading config file")
        print(e)
        db_check_interval = 5

    while True:
        await schedule_exams(bot)
        await asyncio.sleep(db_check_interval)
