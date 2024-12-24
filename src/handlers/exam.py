from datetime import datetime

from aiogram import types, Router, Bot
from aiogram.fsm.context import FSMContext
import os
from dotenv import load_dotenv
from src.database.db_adapter import DatabaseAdapter
from src.objects.exam import Exam
from src.objects.user import User
from src.forms import Form
from src.keyboards.user_keyboards import *
load_dotenv()
router = Router()
adapter = DatabaseAdapter()


@router.callback_query(lambda c: c.data == 'join_exam')
async def join_exam_list(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer()
    message = callback_query.message
    try:
        exams = adapter.get_available_exams()
        if exams:
            response = "Список доступных экзаменов:\n\n"
            for i in range(len(exams)):
                response += f"{i + 1}. Название: {exams[i].name}, Дата и время: {exams[i].timestamp}\n"
            response += "\nНапишите номер экзамена, к которому хотите присоединиться."
            await message.edit_text(response)
            await state.set_state(Form.join_exam_num)
        else:
            await message.edit_text("Нет доступных экзаменов")
    except Exception as e:
        await message.edit_text("Нет доступных экзаменов")


@router.message(Form.join_exam_num)
async def join_exam(message: types.Message, state: FSMContext):
    text = message.text
    telegram_id = message.from_user.id
    user = User(telegram_id)
    exams = adapter.get_available_exams()
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

async def send_consultation_request(bot: Bot, examiner_id, requester_id, requester_name):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text="Принять", callback_data=f"accept_consultation:{requester_id}"),
    ]])

    await bot.send_message(
        examiner_id,
        f"Пользователь {requester_name} запрашивает консультацию. Принять или отклонить?",
        reply_markup=keyboard
    )


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
                await message.answer("Уведомление отправлено всем экзаменаторам.")
            else:
                await message.answer("Вы не участвуете в этом экзамене.")
        else:
            await message.answer("Вы не зарегистрированы на экзамен.")
    else:
        await message.answer("Вы не зарегистрированы в системе.")


@router.message(lambda message: message.text == "Запросить консультацию")
async def handle_ready_to_answer(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    user = User(telegram_id)
    exam = Exam.get_exam_by_id(user.get_registered_exam())
    bot = Bot(str(os.getenv("BOT_API_TOKEN")))
    if exam:
        if exam.examiners:
            await message.answer("Вы запросили консультацию, ждите.", reply_markup=user_exam_reply_keyboard)
            for i in exam.examiners:
                await send_consultation_request(bot, i, telegram_id, message.from_user.full_name)
        else:
            await message.answer("Нет доступных экзаменаторов для консультации.", reply_markup=user_exam_reply_keyboard)
    else:
        await message.answer("Экзамен не найден.", reply_markup=user_exam_reply_keyboard)



@router.callback_query(lambda c: c.data.startswith("accept_consultation"))
async def accept_consultation(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback_query.answer()
    examiner_id = callback_query.from_user.id
    data = callback_query.data.split(":")
    student_id = data[1]

    student = User(student_id)
    examiner = User(examiner_id)

    await bot.send_message(chat_id=student_id, text=f"Ваш запрос на консультацию принят экзаменатором {examiner.name}.")
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
                                message_id=callback_query.message.message_id)
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


@router.message(lambda message: message.text == "Покинуть экзамен")
async def confirm_leave_exam(message: types.Message, state: FSMContext):
    await message.answer("Вы уверены, что хотите покинуть экзамен?", reply_markup=confirm_leave_exam_keyboard_1)


@router.message(lambda message: message.text == "Да, я уверен")
async def confirm_leave_exam_step_2(message: types.Message, state: FSMContext):
    await message.answer("Вы точно уверены, что хотите покинуть экзамен?", reply_markup=confirm_leave_exam_keyboard_2)


@router.message(lambda message: message.text == "Нет, я передумал")
async def cancel_leave_exam(message: types.Message, state: FSMContext):
    await message.answer("Вы остались в экзамене.", reply_markup=user_exam_reply_keyboard)


@router.message(lambda message: message.text == "Нет, я все же передумал")
async def cancel_leave_exam(message: types.Message, state: FSMContext):
    await message.answer("Вы остались в экзамене.", reply_markup=user_exam_reply_keyboard)


@router.message(lambda message: message.text == "Да, я точно-точно уверен")
async def leave_exam_final(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    user = User(telegram_id)
    exam = Exam.get_exam_by_id(user.registered_exam_id)
    exam.remove_participant(telegram_id)
    user.set_registered_exam(None)
    await message.answer(f"Вы успешно покинули экзамен {exam.name}", reply_markup=user_main_menu_keyboard)
