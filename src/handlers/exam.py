from aiogram import types, Router, Bot
from aiogram.fsm.context import FSMContext

from src.objects.exam import Exam
from src.objects.user import User
from src.forms import Form
from src.keyboards.user_keyboards import *
from src.keyboards.admin_keyboards import *

router = Router()


@router.callback_query(lambda c: c.data == 'join_exam')
async def join_exam_list(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer()
    message = callback_query.message
    try:
        exams = Exam.get_all_exams()
        if exams:
            response = "Список доступных экзаменов:\n\n"
            for i in range(len(exams)):
                response += f"{i + 1}. Название: {exams[i].name}, Дата и время: {exams[i].timestamp}\n"
            response += "\nНапишите номер экзамена, к которому хотите присоединиться."
            await message.edit_text(response)
            await state.set_state(Form.edit_exam_num)
        else:
            await message.edit_text("Нет доступных экзаменов")
    except Exception as e:
        await message.edit_text("Нет доступных экзаменов")


@router.message(Form.join_exam_num)
async def join_exam(message: types.Message, state: FSMContext):
    text = message.text
    telegram_id = message.from_user.id
    user = User(telegram_id)
    exams = Exam.get_all_exams()
    if (not text.isdigit()) or int(text) > len(exams):
        await message.answer("Экзамен не найден")
    else:
        await state.clear()
        exam_id = exams[int(text) - 1].id
        telegram_id = message.from_user.id
        exam = Exam.get_exam_by_id(exam_id)
        exam.add_participant(str(telegram_id))
        user.set_registered_exam(exam_id)
        await message.answer(f"Вы успешно присоединились к экзамену {exam.name}", reply_markup=user_leave_exam_keyboard)


@router.callback_query(lambda c: c.data == 'leave_exam')
async def leave_exam(callback_query: types.CallbackQuery):
    await callback_query.answer()
    message = callback_query.message
    telegram_id = callback_query.from_user.id
    user = User(telegram_id)
    exam = Exam.get_exam_by_id(user.registered_exam_id)
    exam.remove_participant(telegram_id)
    user.set_registered_exam(None)
    await message.edit_text(f"Вы успешно покинули экзамен {exam.name}", reply_markup=user_main_menu_keyboard)


@router.callback_query(lambda c: c.data == 'request_consultation')
async def handle_ready_to_answer(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    telegram_id = callback_query.from_user.id
    message = callback_query.message
    user = User(telegram_id)
    exam = Exam.get_exam_by_id(user.get_registered_exam())
    if exam:
        if exam.examiners:
            response = "Список доступных экзаменаторов:\n"
            for idx, examiner_id in enumerate(exam.examiners, start=1):
                examiner = User(examiner_id)
                response += f"{idx}. {examiner.name}\n"
            response += "Введите номер экзаменатора для запроса консультации:"
            await message.edit_text(response)
            await state.set_state(Form.awaiting_examiner_number)
        else:
            await message.edit_text("Нет доступных экзаменаторов для консультации.", reply_markup=user_exam_keyboard)
    else:
        await message.edit_text("Экзамен не найден.", reply_markup=user_exam_keyboard)


async def send_consultation_request(bot: Bot, examiner_id, requester_id, requester_name):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text="Принять", callback_data=f"accept_consultation:{requester_id}"),
        types.InlineKeyboardButton(text="Отклонить", callback_data=f"decline_consultation:{requester_id}")
    ]])

    await bot.send_message(
        examiner_id,
        f"Пользователь {requester_name} запрашивает консультацию. Принять или отклонить?",
        reply_markup=keyboard
    )


@router.message(Form.awaiting_examiner_number)
async def process_examiner_number(message: types.Message, state: FSMContext):
    try:
        examiner_number = int(message.text)
        print(f"Выбранный номер экзаменатора: {examiner_number}")
        telegram_id = message.from_user.id
        user = User(telegram_id)
        exam = Exam.get_exam_by_id(user.get_registered_exam())
        if 1 <= examiner_number <= len(exam.examiners):
            examiner_id = exam.examiners[examiner_number - 1]
            await send_consultation_request(message.bot, examiner_id, message.from_user.id, message.from_user.full_name)
            await message.answer("Запрос на консультацию отправлен экзаменатору.")
            await state.clear()
        else:
            await message.answer("Неверный номер экзаменатора. Пожалуйста, попробуйте снова.")
    except ValueError as e:
        print(e)
        await message.answer("Пожалуйста, введите корректный номер экзаменатора.")


@router.callback_query(lambda c: c.data.startswith("accept_consultation"))
async def accept_consultation(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    examiner_id = callback_query.from_user.id
    data = callback_query.data.split(":")
    student_id = data[1]

    student = User(student_id)
    examiner = User(examiner_id)

    await bot.edit_message_text(chat_id=student_id, text=f"Ваш запрос на консультацию принят экзаменатором {examiner.name}.", reply_markup=user_exam_keyboard, message_id=callback_query.message.message_id)
    await bot.edit_message_text(chat_id=examiner_id, text=f"Вы приняли запрос на консультацию от {student.name}.", message_id=callback_query.message.message_id)


@router.callback_query(lambda c: c.data.startswith("decline_consultation"))
async def decline_consultation(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    examiner_id = callback_query.from_user.id
    data = callback_query.data.split(":")
    student_id = data[1]

    student = User(student_id)
    examiner = User(examiner_id)

    await bot.edit_message_text(chat_id=student_id,
                                text=f"Ваш запрос на консультацию отклонен экзаменатором {examiner.name}.",
                                reply_markup=user_exam_keyboard, message_id=callback_query.message.message_id)
    await bot.edit_message_text(chat_id=examiner_id,
                                text=f"Вы отклонили запрос на консультацию от {student.name}.",
                                message_id=callback_query.message.message_id)


@router.callback_query(lambda c: c.data.startswith("accept_student"))
async def handle_accept_student(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    examiner_id = callback_query.from_user.id
    await callback_query.answer()
    action, student_id, exam_id = callback_query.data.split(":")
    exam = Exam.get_exam_by_id(exam_id)
    if exam:
        if exam.is_student_assigned(student_id):
            await bot.edit_message_text(chat_id=examiner_id, text="Ученик уже назначен другому экзаменатору.", message_id=callback_query.message.message_id)
        else:
            exam.assign_student_to_examiner(student_id, examiner_id)
            student = User(student_id)
            examiner = User(examiner_id)
            await bot.send_message(examiner_id, f"Вы назначены персональным экзаменатором для ученика {student.name}.")
            await bot.send_message(student_id, f"Вам назначен персональный экзаменатор {examiner.name}.")

            data = await state.get_data()
            message_ids = data.get('message_ids', [])
            for ex_id, msg_id in message_ids:
                if str(ex_id) != str(examiner_id):
                    await bot.edit_message_text("Ученик уже назначен другому экзаменатору.", chat_id=ex_id, message_id=msg_id)
                else:
                    await bot.edit_message_text("Вы приняли ученика.", chat_id=ex_id, message_id=msg_id)
    else:
        await bot.send_message(examiner_id, "Экзамен не найден.")

    await callback_query.answer()


async def send_ready_notification(bot: Bot, examiner_id, student_id, student_name, exam_id):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Принять", callback_data=f"accept_student:{student_id}:{exam_id}")]
    ])

    message = await bot.send_message(
        examiner_id,
        f"Ученик {student_name} готов отвечать. Хотите принять его?",
        reply_markup=keyboard
    )

    return message.message_id


@router.message(lambda message: message.text == "Готов отвечать")
async def ready_to_answer_command(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    user = User(telegram_id)
    if user.exists():
        if user.registered_exam_id:
            exam = Exam.get_exam_by_id(user.registered_exam_id)
            if exam and str(telegram_id) in exam.participants:
                message_ids = []
                for examiner_id in exam.examiners:
                    message_id = await send_ready_notification(message.bot, examiner_id, telegram_id, user.name, user.registered_exam_id)
                    message_ids.append((examiner_id, message_id))
                await state.update_data(message_ids=message_ids)
                await message.reply("Уведомление отправлено всем экзаменаторам.")
            else:
                await message.reply("Вы не участвуете в этом экзамене.")
        else:
            await message.reply("Вы не зарегистрированы на экзамен.")
    else:
        await message.reply("Вы не зарегистрированы в системе.")
