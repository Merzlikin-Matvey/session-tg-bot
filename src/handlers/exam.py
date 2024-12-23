from aiogram import types, Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.objects.exam import Exam
from src.objects.user import User
from src.forms import Form

router = Router()


@router.message(Command('exam_list'))
async def exam_list_command(message: types.Message):
    exams = Exam.get_all_exams()
    if exams:
        response = "Список доступных экзаменов:\n"
        for exam in exams:
            response += f"Название: {exam.name}, Дата и время: {exam.timestamp}, Команда для присоединения: /join_exam_{exam.id}\n"
        await message.reply(response)
    else:
        await message.reply("Нет доступных экзаменов")


@router.message(lambda message: message.text and message.text.startswith('/join_exam_'))
async def join_exam_command(message: types.Message, state: FSMContext):
    command = message.text
    exam_id = int(command.split('_')[-1])
    telegram_id = message.from_user.id
    user = User(telegram_id)

    if user.get_registered_exam():
        await message.reply("Вы уже зарегистрированы на другой экзамен. Сначала выйдите из текущего экзамена.")
        return

    exam = Exam.get_exam_by_id(exam_id)
    if exam:
        if str(telegram_id) in exam.participants:
            await message.reply("Вы уже присоединились к этому экзамену")
        else:
            exam.add_participant(str(telegram_id))
            user.set_registered_exam(exam_id)
            await message.reply("Вы успешно присоединились к экзамену!")
    else:
        await message.reply("Экзамен не найден.")

@router.message(Command('leave_all_exams'))
async def leave_all_exams_command(message: types.Message):
    telegram_id = message.from_user.id
    user = User(telegram_id)

    all_exams = Exam.get_all_exams()
    for exam in all_exams:
        if str(telegram_id) in exam.participants:
            exam.remove_participant(str(telegram_id))
    user.set_registered_exam(None)
    await message.reply("Вы успешно покинули все экзамены.")

@router.message(lambda message: message.text and message.text.startswith('/request_consultation_'))
async def request_consultation_command(message: types.Message, state: FSMContext):
    command = message.text
    exam_id = int(command.split('_')[-1])
    exam = Exam.get_exam_by_id(exam_id)
    if exam:
        if not exam.examiners:
            await message.reply("Нет доступных экзаменаторов для консультации.")
            return

        response = "Список доступных экзаменаторов:\n"
        for idx, examiner_id in enumerate(exam.examiners, start=1):
            examiner = User(examiner_id)
            response += f"{idx}. {examiner.name} (ID: {examiner_id})\n"
        response += "Введите номер экзаменатора для запроса консультации:"
        await message.reply(response)
        await state.update_data(exam_id=exam_id)
        await state.set_state(Form.awaiting_examiner_number)
    else:
        await message.reply("Экзамен не найден.")


async def send_consultation_request(bot: Bot, examiner_id, requester_id, requester_name):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Принять", callback_data=f"accept_consultation:{requester_id}")],
        [types.InlineKeyboardButton(text="Отклонить", callback_data=f"decline_consultation:{requester_id}")]
    ])

    await bot.send_message(
        examiner_id,
        f"Пользователь {requester_name} запрашивает консультацию. Принять или отклонить?",
        reply_markup=keyboard
    )


@router.message(Form.awaiting_examiner_number)
async def process_examiner_number(message: types.Message, state: FSMContext):
    try:
        examiner_number = int(message.text)
        data = await state.get_data()
        exam_id = data['exam_id']
        exam = Exam.get_exam_by_id(exam_id)

        if 1 <= examiner_number <= len(exam.examiners):
            examiner_id = exam.examiners[examiner_number - 1]
            await send_consultation_request(message.bot, examiner_id, message.from_user.id, message.from_user.full_name)
            await message.reply("Запрос на консультацию отправлен экзаменатору.")
            await state.clear()
        else:
            await message.reply("Неверный номер экзаменатора. Пожалуйста, попробуйте снова.")
    except ValueError as e:
        print(e)
        await message.reply("Пожалуйста, введите корректный номер экзаменатора.")


@router.callback_query(lambda c: c.data.startswith("accept_student"))
async def handle_accept_student(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    examiner_id = callback_query.from_user.id
    action, student_id, exam_id = callback_query.data.split(":")

    exam = Exam.get_exam_by_id(exam_id)
    if exam:
        if exam.is_student_assigned(student_id):
            await bot.send_message(examiner_id, "Вы опоздали, ученик уже назначен другому экзаменатору.")
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

@router.message(Command('ready_to_answer'))
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

