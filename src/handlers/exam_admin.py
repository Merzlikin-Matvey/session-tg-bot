from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from src.user import User
from src.exam import Exam
from src.forms import Form

router = Router()

@router.message(Command('add_exam'))
async def add_exam_command(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    user = User(telegram_id)
    if user.is_admin:
        await message.reply("Пожалуйста, введите название экзамена:")
        await state.set_state(Form.awaiting_exam_name)
    else:
        await message.reply("У вас нет прав для добавления экзамена.")

@router.message(Form.awaiting_exam_name)
async def process_exam_name(message: types.Message, state: FSMContext):
    exam_name = message.text
    await state.update_data(exam_name=exam_name)
    await message.reply("Пожалуйста, введите дату и время начала экзамена (в формате ГГГГ-ММ-ДД ЧЧ:ММ):")
    await state.set_state(Form.awaiting_exam_datetime)

@router.message(Form.awaiting_exam_datetime)
async def process_exam_datetime(message: types.Message, state: FSMContext):
    exam_datetime_str = message.text
    try:
        exam_datetime = datetime.strptime(exam_datetime_str, "%Y-%m-%d %H:%M")
        data = await state.get_data()
        exam_name = data['exam_name']
        exam = Exam(exam_name, exam_datetime)
        exam.save()
        await message.reply("Экзамен успешно добавлен!")
        await state.clear()
    except ValueError:
        await message.reply("Неверный формат даты и времени. Пожалуйста, попробуйте снова (в формате ГГГГ-ММ-ДД ЧЧ:ММ):")