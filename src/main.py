import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
import os

from src.user import User

load_dotenv()

API_TOKEN = os.getenv('BOT_API_TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

class Form(StatesGroup):
    awaiting_full_name = State()

@router.message(Command('start'))
async def send_welcome(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    user = User(telegram_id)
    if not user.exists():
        await message.reply("Пожалуйста, введите фамилию и имя:")
        await state.set_state(Form.awaiting_full_name)
    else:
        await message.reply("Привет! Добро пожаловать в нашего бота")

@router.message(Form.awaiting_full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    full_name = message.text
    telegram_id = message.from_user.id
    user = User(telegram_id)
    user.add(full_name)
    await message.reply("Спасибо! Ваши данные сохранены")
    await state.clear()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())