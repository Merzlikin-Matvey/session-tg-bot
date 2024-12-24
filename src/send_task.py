import logging
from aiogram import Bot
from aiogram.types import FSInputFile
import numpy as np

from src.objects.exam import Exam
from src.keyboards.user_keyboards import *
from src.keyboards.admin_keyboards import *

logging.basicConfig(level=logging.INFO)


async def send_task_image(bot: Bot, telegram_id: int, image_path: str):
    try:
        photo_file = FSInputFile(path=image_path)
        await bot.send_photo(chat_id=telegram_id, photo=photo_file)
        await bot.send_message(chat_id=telegram_id, text="Ваш билет", reply_markup=user_exam_reply_keyboard)
        logging.info(f"Отправлено изображение: {image_path}")
    except Exception as e:
        logging.error(f"Неизвестная ошибка при отправке изображения: {e}")


async def send_tasks_for_all_users(bot: Bot, exam: Exam):
    participants = exam.participants
    tasks_paths = exam.tasks_paths
    if not tasks_paths:
        for telegram_id in participants:
            await bot.send_message(chat_id=telegram_id, text="Извините, но задачи для экзамена отсутствуют.", reply_markup=user_exam_reply_keyboard)
        return
    if len(tasks_paths) < 3:
        for telegram_id in participants:
            await bot.send_message(chat_id=telegram_id, text="Извините, но недостаточно задач для экзамена.", reply_markup=user_exam_reply_keyboard)
        return
    tasks_paths = tasks_paths.split(';')

    if isinstance(tasks_paths, str):
        tasks_paths = [tasks_paths]

    np.random.shuffle(tasks_paths)

    if len(tasks_paths) == 0:
        logging.error("Нет задач для отправки")
    else:
        for i, telegram_id in enumerate(participants):
            task_path = tasks_paths[i % len(tasks_paths)]
            await send_task_image(bot, telegram_id, task_path)
