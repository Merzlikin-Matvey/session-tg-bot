import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os
from handlers import start, exam_admin, admin

load_dotenv()

API_TOKEN = os.getenv('BOT_API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(exam_admin.router)
dp.include_router(admin.router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    print("Bot started")