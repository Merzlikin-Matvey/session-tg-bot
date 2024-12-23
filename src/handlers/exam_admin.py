from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from src.objects.user import User
from src.objects.exam import Exam
from src.forms import Form
from src.tasks.save import save_task_image,save_task_pdf,save_task_zip,save_task_rar
from aiogram import Bot
import uuid

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
        print(state.get_data())
        await message.reply("Пожалуйста, отправьте файлы, изображения или задачи текстом.")
        await state.set_state(Form.awaiting_task_image)
    else:
        await message.reply("У вас нет прав для добавления задач.")

@router.message(Form.awaiting_task_image)
async def process_task_image(message: types.Message, state: FSMContext, bot: Bot):
    while  message.text != "/stop_adding":
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
        if message.content_type == types.ContentType.DOCUMENT:
            data = await state.get_data()
            print(data)
            exam_id = data['exam_id']
            if '.pdf' in message.document.file_name:
                save_path = await save_task_pdf(bot, message.document.file_id, exam_id)
                exam = Exam.get_exam_by_id(exam_id)
                exam.add_task(save_path)
            if '.zip' in message.document.file_name:
                save_path = await save_task_zip(bot, message.document.file_id, exam_id)

            if '.rar' in message.document.file_name:
                save_path = await save_task_rar(bot, message.document.file_id, exam_id)

    else:
        await message.reply("Добавление задач остановлено.")
        await state.clear()

