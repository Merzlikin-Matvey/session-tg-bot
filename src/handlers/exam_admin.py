from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from src.objects.user import User
from src.objects.exam import Exam
from src.forms import Form
from src.tasks.save import save_task_image, save_task_pdf, save_task_zip, save_task_rar
from src.keyboards.admin_keyboards import *
from aiogram import Bot
from aiogram.types import FSInputFile


router = Router()


async def sort_upcoming_exams(exams):
    current_time = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
    upcoming_exams = [exam for exam in exams if datetime.strptime(str(exam.timestamp), "%Y-%m-%d %H:%M:%S").timestamp() >= current_time.timestamp()]
    return sorted(upcoming_exams, key=lambda exam: exam.timestamp)


@router.callback_query(lambda c: c.data == 'add_exam')
async def add_exam_command(callback_query: types.CallbackQuery, state: FSMContext):
    print("GO")
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
        await message.answer("Экзамен успешно добавлен!", reply_markup=admin_edit_exam_keyboard)
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
        exams = await sort_upcoming_exams(exams)
        if exams:
            response = "Список доступных экзаменов:\n\n"
            for i in range(len(exams)):
                response += f"{i + 1}. Название: {exams[i].name}, Дата и время: {exams[i].timestamp}\n"
            response += "\nНапишите номер экзамена, который хотите изменить."
            await message.edit_text(response, reply_markup=admin_create_exam_keyboard)
            await state.set_state(Form.edit_exam_num)
            state = await state.get_state()
            print("State", state)
        else:
            await message.edit_text("Нет доступных экзаменов")
    except Exception as e:
        await message.edit_text("Нет доступных экзаменов")


@router.message(Form.edit_exam_num)
async def process_exam_datetime(message: types.Message, state: FSMContext):
    exam_num = int(message.text)
    exams = Exam.get_all_exams()
    if exam_num < 1 or exam_num > len(exams):
        await message.edit_text("Неверный номер экзамена.")
        return
    exam_id = exams[exam_num - 1].id
    await state.update_data(exam_id=exam_id)
    # Если уже в комиссии, показываем другую клавиатуру
    await message.answer("Выберите действие:", reply_markup=admin_edit_exam_keyboard_1)


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

        exam = Exam.get_exam_by_id(exam_id)
        if isinstance(save_path, str):
            save_path = [save_path]
        for path in save_path:
            exam.add_task(path)
        files_received += len(save_path)

    else:
        await state.clear()
        await message.answer("Добавление задач завершено.", reply_markup=types.ReplyKeyboardRemove())
        exams = Exam.get_all_exams()
        if exams:
            response = "Список доступных экзаменов:\n\n"
            for i in range(len(exams)):
                response += f"{i + 1}. Название: {exams[i].name}, Дата и время: {exams[i].timestamp}\n"
            response += "\nНапишите номер экзамена, который хотите изменить."
            await message.answer(response, reply_markup=admin_create_exam_keyboard)
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


@router.message(lambda message: message.text and message.text.startswith('/view_exam_tickets_'))
async def view_exam_tickets(message: types.Message):
    try:
        telegram_id = message.from_user.id
        user = User(telegram_id)

        if not user.is_admin:
            await message.reply("У вас нет прав для выполнения этой команды.")
            return
        else:
            exam_id = int(message.text.split('_')[3])
            exams = Exam.get_exam_by_id(exam_id)
            response = "Список учеников:\n\n"
            for i in range(len(exams.participants)):
                user_id = exams.participants[i]
                response += f"{i + 1}.Имя: {User(user_id).name}. Айди:{user_id}. Для просмотра билета ученика напишите /view_ticket_{user_id}\n"
            await message.reply(response)
    except Exception as e:
        print(e)
        await message.reply("Произошла ошибка при просмотре билетов экзамена.")


@router.message(lambda message: message.text and message.text.startswith('/view_ticket_'))
async def view_ticket(message: types.Message):
    try:
        telegram_id = message.from_user.id
        user = User(telegram_id)
        if not user.is_admin:
            await message.reply("У вас нет прав для выполнения этой команды.")
            return
        else:
            user_id = int(message.text.split('_')[2])
            user = User(user_id)
            exam = user.get_registered_exam()
            if exam:
                exam = Exam.get_exam_by_id(exam)
                if exam:
                    await message.reply_document(document=FSInputFile("./tasks/exam_1_task_759f2f36-b721-4659-a6af-d4395f56aae8.pdf"))
                else:
                    await message.reply("Экзамен не найден.")
            else:
                await message.reply("Вы не зарегистрированы на экзамен.")

    except Exception as e:
        print(e)
        await message.reply("Произошла ошибка при просмотре билетов экзамена.")
