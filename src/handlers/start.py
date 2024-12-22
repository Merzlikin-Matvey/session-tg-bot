from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.user import User
from src.forms import Form

router = Router()

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
    user.save()
    await message.reply("Спасибо! Ваши данные сохранены")
    await state.clear()