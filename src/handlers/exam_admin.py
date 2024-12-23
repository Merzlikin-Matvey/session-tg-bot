from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from src.objects.user import User
from src.objects.exam import Exam
from src.forms import Form
from src.tasks.save import save_task_image, save_task_pdf, save_task_zip, save_task_rar
from src.keyboards.user_keyboards import *
from src.keyboards.admin_keyboards import *
from aiogram import Bot

router = Router()


@router.callback_query(lambda c: c.data == 'add_exam') 
async def add_exam_command(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    callback_query.answer()
    message = callback_query.message
    user = User(telegram_id)
    if user.is_admin:
        await message.edit_text("Пожалуйста, введите название экзамена:")
        await state.set_state(Form.awaiting_exam_name)
    else:
        await message.edit_text("У вас нет прав для добавления экзамена.", reply_markup=admin_main_menu_keyboard)


@router.message(Form.awaiting_exam_name)
async def process_exam_name(message: types.Message, state: FSMContext):
    exam_name = message.text
    await state.update_data(exam_name=exam_name)
    await message.answer("Пожалуйста, введите дату и время начала экзамена (в формате ДД.ММ.ГГ ЧЧ:ММ):")
    await state.set_state(Form.awaiting_exam_datetime)


@router.message(Form.awaiting_exam_datetime)
async def process_exam_datetime(message: types.Message, state: FSMContext):
    exam_datetime_str = message.text
    try:
        exam_datetime = datetime.strptime(exam_datetime_str, "%d.%m.%y %H:%M")
        data = await state.get_data()
        exam_name = data['exam_name']
        exam = Exam(exam_name, exam_datetime)
        exam.save()
        await message.answer("Экзамен успешно добавлен!", reply_markup=admin_main_menu_keyboard)
        await state.clear()
    except ValueError as e:
        print("ValueError")
        print(e)
        await message.reply("Неверный формат даты и времени. Пожалуйста, попробуйте снова (в формате ДД.ММ.ГГ ЧЧ:ММ):")

@router.callback_query(lambda c: c.data == 'edit_exam')
async def edit_exam(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer()
    message = callback_query.message
    try:
        exams = Exam.get_all_exams()
        if exams:
            response = "Список доступных экзаменов:\n\n"
            for i in range(len(exams)):
                response += f"{i + 1}. Название: {exams[i].name}, Дата и время: {exams[i].timestamp}\n"
            response += "\nНапишите номер экзамена, который хотите изменить."
            await message.edit_text(response)
            await state.set_state(Form.join_exam_num)
        else:
            await message.edit_text("Нет доступных экзаменов")
    except:
        await message.edit_text("Нет доступных экзаменов")

@router.message(lambda message: message.text and message.text.startswith('/add_tasks_'))
async def add_tasks_command(message: types.Message, state: FSMContext):
    command = message.text
    exam_id = command.split('_')[-1]
    telegram_id = message.from_user.id
    user = User(telegram_id)
    if user.is_admin:
        await state.update_data(exam_id=exam_id)
        await message.reply("Пожалуйста, отправьте архив,сжатую папку или изображения с задачами для экзамена:")
        await state.set_state(Form.awaiting_task_image)
    else:
        await message.reply("У вас нет прав для добавления задач.")


@router.message(Form.awaiting_task_image)
async def process_task_image(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    print(data)
    exam_id = data['exam_id']

    if message.content_type == types.ContentType.PHOTO:
        photo = message.photo[-1]
        save_path = await save_task_image(bot, photo.file_id, exam_id)
        print(save_path)
        exam = Exam.get_exam_by_id(exam_id)
        exam.add_task(save_path)

        await message.reply(f"Изображение с задачами успешно добавлено! Сохранено как {save_path}")

    elif message.content_type == types.ContentType.DOCUMENT:
        if '.pdf' in message.document.file_name:
            save_path = await save_task_pdf(bot, message.document.file_id, exam_id)
        elif '.zip' in message.document.file_name:
            save_path = await save_task_zip(bot, message.document.file_id, exam_id)
        elif '.rar' in message.document.file_name:
            save_path = await save_task_rar(bot, message.document.file_id, exam_id)
        else:
            await message.reply("Неподдерживаемый формат файла.")
            return

        exam = Exam.get_exam_by_id(exam_id)
        if isinstance(save_path, str):
            save_path = [save_path]
            exam.add_task(save_path)
        else:
            for i in save_path:
                exam.add_task(i)
        await message.reply(f"Файл с задачами успешно добавлен! Сохранено как {",".join(save_path)}")

    else:
        await message.reply("Добавление задач завершено.")
        await state.clear()


@router.message(lambda message: message.text and message.text.startswith('/add_examiner_'))
async def add_examiner(message: types.Message):
    try:
        telegram_id = message.from_user.id
        user = User(telegram_id)

        if not user.is_admin:
            await message.reply("У вас нет прав для выполнения этой команды.")
            return

        command = message.text
        parts = command.split('_')
        if len(parts) != 3:
            await message.reply("Использование: /add_examiner_{exam_id}")
            return

        exam_id = int(parts[2])

        exam = Exam.get_exam_by_id(exam_id)
        if not exam:
            await message.reply("Экзамен с указанным ID не найден.")
            return

        exam.add_examiner(telegram_id)
        await message.reply(f"Вы добавлены в экзамен {exam_id} в качестве экзаменатора.")

    except Exception as e:
        print(e)
        await message.reply("Произошла ошибка при добавлении экзаменатора.")
