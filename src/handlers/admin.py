from http.client import responses

from aiogram import types, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from datetime import datetime

from src.database.db_adapter import DatabaseAdapter
from src.objects.user import User
from src.objects.exam import Exam
from src.forms import Form
from src.tasks.save import save_task_image, save_task_pdf, save_task_zip, save_task_rar
from src.keyboards.admin_keyboards import *
from aiogram import Bot
from aiogram.types import FSInputFile


router = Router()
adapter = DatabaseAdapter()


@router.callback_query(lambda c: c.data == 'admin_main_menu')
async def admin_main_menu(callback_query: types.CallbackQuery):
    await callback_query.answer()
    message = callback_query.message
    await message.edit_text("Выберите действие:", reply_markup=admin_main_menu_keyboard)


@router.callback_query(lambda c: c.data == 'add_exam')
async def add_exam_command(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    await callback_query.answer()
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
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать экзамен", callback_data="add_exam")]
    ])
    try:
        exams = adapter.get_recent_exams()
        if exams:
            response = "Список доступных экзаменов:\n\n"
            for i in range(len(exams)):
                response += f"{i + 1}. Название: {exams[i].name}, Дата и время: {exams[i].timestamp}\n"
            response += "\nНапишите номер экзамена, который хотите изменить."
            await message.edit_text(response, reply_markup=keyboard)
            await state.set_state(Form.edit_exam_num)
        else:
            await message.edit_text("Нет доступных экзаменов", reply_markup=keyboard)
    except Exception as e:
        await message.edit_text("Нет доступных экзаменов", reply_markup=keyboard)


@router.message(Form.edit_exam_num)
async def process_exam_datetime(message: types.Message, state: FSMContext):
    examiner_id = str(message.from_user.id)
    exam_num = int(message.text)
    exams = adapter.get_recent_exams()
    if exam_num < 1 or exam_num > len(exams):
        await message.edit_text("Неверный номер экзамена.")
        return
    exam = exams[exam_num - 1]
    await state.update_data(exam_id=exam.id)
    admin_edit_exam_keyboard_1 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Посмотреть задания", callback_data=f"see_tasks_{exam.id}")],
        [InlineKeyboardButton(text="Добавить задания", callback_data="add_task")],
        [InlineKeyboardButton(text="Вступить в экзаменационную комиссию", callback_data=f"become_teacher_{exam.id}")],
        [InlineKeyboardButton(text="К списку экзаменов", callback_data="edit_exam")]
    ])
    admin_edit_exam_keyboard_2 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Посмотреть задания", callback_data=f"see_tasks_{exam.id}")],
        [InlineKeyboardButton(text="Добавить задания", callback_data="add_task")],
        [InlineKeyboardButton(text="Покинуть экзаменационную комиссию", callback_data=f"become_admin_{exam.id}")],
        [InlineKeyboardButton(text="К списку экзаменов", callback_data="edit_exam")]
    ])
    if examiner_id in exam.examiners:
        await message.answer(f"Экзамен {exam.name}:", reply_markup=admin_edit_exam_keyboard_2)
    else:
        await message.answer(f"Экзамен {exam.name}:", reply_markup=admin_edit_exam_keyboard_1)


@router.callback_query(lambda c: c.data.startswith('see_tasks'))
async def see_tasks(callback_query: types.CallbackQuery):
    await callback_query.answer()
    message = callback_query.message
    try:
        command = callback_query.data
        parts = command.split('_')
        exam_id = int(parts[2])

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Получить все задачи", callback_data=f"get_all_tasks_{exam_id}")],
            [InlineKeyboardButton(text="Получить задачи для конкретного пользователя", callback_data=f"get_user_tasks_{exam_id}")]
        ])

        await message.edit_text("Выберите действие:", reply_markup=keyboard)
    except Exception as e:
        print(e)
        await message.answer("Произошла ошибка при просмотре заданий.")


@router.callback_query(lambda c: c.data == 'add_task')
async def add_tasks_command(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    user = User(telegram_id)
    if user.is_admin:
        message = callback_query.message
        await message.edit_text("Пожалуйста, отправьте архив, сжатую папку или изображения с задачами для экзамена:")
        sent_message = await message.answer("Отправляйте ваши файлы и нажмите 'Достаточно!', когда закончите", reply_markup=admin_task_keyboard)
        await state.update_data(message_id=sent_message.message_id)
        await state.set_state(Form.awaiting_task_image)
    else:
        await callback_query.message.reply("У вас нет прав для добавления задач.")


@router.callback_query(lambda c: c.data.startswith('get_all_tasks'))
async def get_all_tasks(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    message = callback_query.message
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться к экзаменам", callback_data="edit_exam")]
    ])

    try:
        command = callback_query.data
        parts = command.split('_')
        exam_id = int(parts[3])

        exam = Exam.get_exam_by_id(exam_id)

        if len(exam.tasks_paths) == 0:
            await message.answer("Задачи для экзамена отсутствуют.", reply_markup=keyboard)
        else:
            tasks = exam.tasks_paths.split(';')
            for task in tasks:
                await message.answer_document(document=FSInputFile(task))
            await message.answer("Все задания успешно отправлены.", reply_markup=keyboard)
    except Exception as e:
        print(e)
        await message.answer("Произошла ошибка при получении всех заданий.", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith('get_user_tasks'))
async def get_user_tasks(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    message = callback_query.message

    try:
        command = callback_query.data
        parts = command.split('_')
        exam_id = int(parts[3])

        exam = Exam.get_exam_by_id(exam_id)
        participants = exam.get_participants()

        response = "Список пользователей:\n\n"
        for i, telegram_id in enumerate(participants):
            user = User(telegram_id)
            response += f"{i + 1}. Пользователь: {user.name}\n"

        response += "\nНапишите номер пользователя, чтобы получить его задания."
        await message.edit_text(response)
        await state.update_data(exam_id=exam_id)
        await state.set_state(Form.awaiting_user_number)
    except Exception as e:
        print(e)
        await message.answer("Произошла ошибка при получении списка пользователей.")


@router.message(Form.awaiting_user_number)
async def process_user_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться к экзаменам", callback_data="edit_exam")]
    ])
    try:
        exam_id = data['exam_id']
        exam = Exam.get_exam_by_id(exam_id)
        participants = exam.get_participants()
        user_num = int(message.text)
        user_id = participants[user_num - 1]

        task = exam.user_tasks[user_id][0]
        if task:
            await message.answer_document(document=FSInputFile(task))
        else:
            await message.answer("Задачи для этого пользователя отсутствуют.")

    except Exception as e:
        print(e)
        await message.answer("Произошла ошибка при получении заданий пользователя.")
    await message.answer("Задачи получены:", reply_markup=keyboard)


@router.message(Form.awaiting_task_image)
async def process_task_image(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    exam_id = data['exam_id']
    message_id = data.get('message_id')
    files_received = data.get('files_received', 0)

    if message.content_type == types.ContentType.PHOTO:
        photo = message.photo[-1]
        save_path = await save_task_image(bot, photo.file_id, exam_id)
        exam = Exam.get_exam_by_id(exam_id)
        exam.add_task(save_path)
        files_received += 1

    elif message.content_type == types.ContentType.DOCUMENT:
        if '.pdf' in message.document.file_name:
            save_path = await save_task_pdf(bot, message.document.file_id, exam_id)
        elif '.zip' in message.document.file_name:
            save_path = await save_task_zip(bot, message.document.file_id, exam_id)
        elif '.rar' in message.document.file_name:
            save_path = await save_task_rar(bot, message.document.file_id, exam_id)
        else:
            return
        # Добавь .jpg .png etc

        exam = Exam.get_exam_by_id(exam_id)
        if isinstance(save_path, str):
            save_path = [save_path]
        for path in save_path:
            exam.add_task(path)
        files_received += len(save_path)

    else:
        await state.clear()
        await message.answer("Добавление задач завершено.", reply_markup=types.ReplyKeyboardRemove())
        exams = adapter.get_recent_exams()
        if exams:
            response = "Список доступных экзаменов:\n\n"
            for i in range(len(exams)):
                response += f"{i + 1}. Название: {exams[i].name}, Дата и время: {exams[i].timestamp}\n"
            response += "\nНапишите номер экзамена, который хотите изменить."

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Создать экзамен", callback_data="add_exam")]
            ])

            await message.answer(response, reply_markup=keyboard)
            await state.set_state(Form.edit_exam_num)
        else:
            await message.answer("Нет доступных экзаменов")

        return

    await state.update_data(files_received=files_received)
    # TODO! Сломалось
    # await bot.edit_message_text(
    #     chat_id=message.chat.id,
    #     message_id=message_id,
    #     text=f"Пожалуйста, отправьте архив, сжатую папку или изображения с задачами для экзамена:\n\nПолучено файлов: {files_received}"
    # )


@router.callback_query(lambda c: c.data.startswith('become_teacher'))
async def become_teacher(callback_query: types.CallbackQuery):
    await callback_query.answer()
    message = callback_query.message
    try:
        telegram_id = callback_query.from_user.id
        user = User(telegram_id)

        command = callback_query.data
        parts = command.split('_')
        exam_id = int(parts[2])

        exam = Exam.get_exam_by_id(exam_id)

        exam.add_examiner(telegram_id)
        admin_edit_exam_keyboard_2 = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться к редактированию", callback_data="edit_exam")],
            [InlineKeyboardButton(text="Покинуть экзаменационную комиссию", callback_data=f"become_admin_{exam.id}")]
        ])
        await message.edit_text(f"Вы добавлены в экзамен {exam.name} в качестве экзаменатора.", reply_markup=admin_edit_exam_keyboard_2)

    except Exception as e:
        print(e)
        await message.answer("Произошла ошибка при добавлении экзаменатора.")


@router.callback_query(lambda c: c.data.startswith('become_admin'))
async def become_teacher(callback_query: types.CallbackQuery):
    await callback_query.answer()
    message = callback_query.message
    try:
        telegram_id = callback_query.from_user.id
        user = User(telegram_id)

        command = callback_query.data
        parts = command.split('_')
        exam_id = int(parts[2])

        exam = Exam.get_exam_by_id(exam_id)

        exam.remove_examiner(telegram_id)
        admin_edit_exam_keyboard_1 = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться к редактированию", callback_data="edit_exam")],
            [InlineKeyboardButton(text="Вступить в экзаменационную комиссию", callback_data=f"become_teacher_{exam.id}")]
        ])
        await message.edit_text(f"Вы больше не экзаменатор в {exam.name}.", reply_markup=admin_edit_exam_keyboard_1)

    except Exception as e:
        print(e)
        await message.answer("Произошла ошибка при удалении экзаменатора.")

@router.message(Command(commands=["make_admin"]))
async def make_admin_command(message: types.Message, command: CommandObject, state: FSMContext):
    try:
        telegram_id = message.from_user.id
        user = User(telegram_id)
        if user.is_admin:
            if len(command.args) == 0:
                await message.answer("Пожалуйста, укажите telegram_id пользователя.")
                return
            target_telegram_id = command.args
            target_user = User(target_telegram_id)
            if target_user.exists():
                target_user.is_admin = True
                target_user.save()
                await message.answer(f"Пользователь {target_user.name} теперь администратор.")
            else:
                await message.answer("Пользователь не найден.")
        else:
            await message.answer("У вас нет прав для выполнения этой команды.")
    except Exception as e:
        print(e)
        await message.answer("Произошла ошибка при добавлении администратора.")

