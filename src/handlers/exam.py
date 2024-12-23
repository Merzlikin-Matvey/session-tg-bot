from aiogram import types, Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.objects.exam import Exam
from src.objects.user import User
from src.forms import Form

router = Router()


@router.callback_query(lambda c: c.data == 'join_exam') 
async def join_exam_list(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer()
    message = callback_query.message
    exams = Exam.get_all_exams()
    if exams:
        response = "Список доступных экзаменов:\n\n"
        for i in range(len(exams)):
            response += f"{i + 1}. Название: {exams[i].name}, Дата и время: {exams[i].timestamp}\n"
        response += "\nНапишите номер экзамена, к которому хотите присоединиться."
        await message.edit_text(response)
        await state.set_state(Form.join_exam_num)
    else:
        await message.edit_text("Нет доступных экзаменов")

@router.message(Form.join_exam_num)
async def join_exam(message: types.Message, state: FSMContext):
    text = message.text
    exams = Exam.get_all_exams()
    if (not text.isdigit()) or int(text) > len(exams):
        await message.answer("Экзамен не найден.")
    exam_id = exams[int(text) - 1].id
    telegram_id = message.from_user.id
    exam = Exam.get_exam_by_id(exam_id)
    if str(telegram_id) in exam.participants:
        await message.answer("Вы уже присоединились к этому экзамену.")
    else:
        exam.add_participant(str(telegram_id))
        await message.answer(f"Вы успешно присоединились к экзамену {exam.name}!")

@router.message(lambda message: message.text and message.text.startswith('/join_exam_'))
async def join_exam_command(message: types.Message):
    command = message.text
    exam_id = int(command.split('_')[-1])
    telegram_id = message.from_user.id
    exam = Exam.get_exam_by_id(exam_id)
    if exam:
        if str(telegram_id) in exam.participants:
            await message.reply("Вы уже присоединились к этому экзамену")
        else:
            exam.add_participant(str(telegram_id))
            await message.reply("Вы успешно присоединились к экзамену!")
    else:
        await message.reply("Экзамен не найден.")


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


@router.callback_query(lambda c: c.data.startswith("accept_consultation") or c.data.startswith("decline_consultation"))
async def handle_consultation_response(callback_query: types.CallbackQuery, bot: Bot):
    examiner_id = callback_query.from_user.id
    action, requester_id = callback_query.data.split(":")

    if action == "accept_consultation":
        await bot.send_message(examiner_id, "Вы приняли запрос на консультацию.")
        await bot.send_message(requester_id, "Ваш запрос на консультацию был принят.")
    elif action == "decline_consultation":
        await bot.send_message(examiner_id, "Вы отклонили запрос на консультацию.")
        await bot.send_message(requester_id, "Ваш запрос на консультацию был отклонен.")

    await callback_query.answer()
