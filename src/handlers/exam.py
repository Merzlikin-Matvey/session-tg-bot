from aiogram import types, Router
from aiogram.filters import Command
from src.objects.exam import Exam

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