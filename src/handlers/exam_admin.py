from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from src.objects.user import User
from src.objects.exam import Exam
from src.forms import Form
from src.tasks.save import save_task_image
from aiogram import Bot

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
    except ValueError as e:
        print("ValueError")
        print(e)
        await message.reply("Неверный формат даты и времени. Пожалуйста, попробуйте снова (в формате ГГГГ-ММ-ДД ЧЧ:ММ):")

@router.message(lambda message: message.text and message.text.startswith('/add_tasks_'))
async def add_tasks_command(message: types.Message, state: FSMContext):
    command = message.text
    exam_id = command.split('_')[-1]
    telegram_id = message.from_user.id
    user = User(telegram_id)
    if user.is_admin:
        await state.update_data(exam_id=exam_id)
        await message.reply("Пожалуйста, отправьте изображение с задачами для экзамена:")
        await state.set_state(Form.awaiting_task_image)
    else:
        await message.reply("У вас нет прав для добавления задач.")

@router.message(Form.awaiting_task_image)
async def process_task_image(message: types.Message, state: FSMContext, bot: Bot):
    if message.content_type == types.ContentType.PHOTO:
        photo = message.photo[-1]
        data = await state.get_data()
        print(data)
        exam_id = data['exam_id']

        save_path = await save_task_image(bot, photo.file_id, exam_id)

        exam = Exam.get_exam_by_id(exam_id)
        exam.add_task(save_path)

        await message.reply(f"Изображение с задачами успешно добавлено! Сохранено как {save_path}")
        await state.clear()
    else:
        await message.reply("Пожалуйста, отправьте изображение.")