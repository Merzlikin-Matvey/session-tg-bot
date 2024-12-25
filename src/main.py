import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os
from src.handlers import start, admin, exam
from src.objects.exam import Exam
from src.schedule import check_new_exams
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

API_TOKEN = os.getenv('BOT_API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(admin.router)
dp.include_router(exam.router)

scheduler = AsyncIOScheduler()

def print_hello():
    print("===============")
    print("Bot is working")
    print("===============")

async def main():
    scheduler.start()
    asyncio.create_task(check_new_exams(bot))
    print_hello()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
