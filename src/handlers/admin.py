from aiogram import types, Router
from aiogram.filters import Command
from src.user import User

router = Router()

@router.message(Command('view_exams'))
async def view_exams_command(message: types.Message):
    telegram_id = message.from_user.id
    user = User(telegram_id)
    if user.is_admin:
        exams = user.get_all_exams()
        if exams:
            response = "Ваши экзамены:\n"
            for exam in exams:
                response += f"Название: {exam.name}, Дата и время: {exam.timestamp}\n"
            await message.reply(response)
        else:
            await message.reply("У вас нет добавленных экзаменов.")
    else:
        await message.reply("У вас нет прав для просмотра экзаменов.")

