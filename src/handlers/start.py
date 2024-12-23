from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.objects.user import User
from src.forms import Form
from src.keyboards.user_keyboards import *
from src.keyboards.admin_keyboards import *

router = Router()


@router.message(Command('start'))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    telegram_id = message.from_user.id
    user = User(telegram_id)
    if not user.exists():
        await message.reply("Пожалуйста, введите фамилию и имя:")
        await state.set_state(Form.awaiting_full_name)
    else:
        print(user.registered_exam_id)
        if user.is_admin:
            await message.answer(f"Привет, {user.name}! Добро пожаловать в нашего бота!", reply_markup=admin_main_menu_keyboard)
        else:
            await message.answer(f"Привет, {user.name}! Добро пожаловать в нашего бота!", reply_markup=user_main_menu_keyboard)


@router.message(Form.awaiting_full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    full_name = message.text
    telegram_id = message.from_user.id
    user = User(telegram_id)
    user.add(full_name)
    user.save()
    if user.is_admin:
        await message.answer("Спасибо! Ваши данные сохранены.", reply_markup=admin_main_menu_keyboard)
    else:
        await message.answer("Спасибо! Ваши данные сохранены.", reply_markup=user_main_menu_keyboard)
