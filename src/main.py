import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os
from src.handlers import start, exam_admin, exam
from src.objects.exam import Exam
from src.schedule import check_new_exams
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

API_TOKEN = os.getenv('BOT_API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(exam_admin.router)
dp.include_router(exam.router)

scheduler = AsyncIOScheduler()


async def main():
    print("Bot started")
    scheduler.start()
    asyncio.create_task(check_new_exams(bot))
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
