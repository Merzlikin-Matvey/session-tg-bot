import os
from aiogram import Bot
import yaml
import uuid
import zipfile


def get_tasks_dir() -> str:
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    tasks_dir = config['tasks_dir']

    return tasks_dir


async def save_task_image(bot: Bot, file_id: str, exam_id: str) -> str:
    uuid_value = str(uuid.uuid4())
    filename = f"exam_{exam_id}_task_{uuid_value}.jpg"
    save_path = os.path.join(get_tasks_dir(), filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, save_path)

    return save_path


async def save_task_pdf(bot: Bot, file_id: str, exam_id: str) -> str:
    uuid_value = str(uuid.uuid4())
    filename = f"exam_{exam_id}_task_{uuid_value}.pdf"
    save_path = os.path.join(get_tasks_dir(), filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, save_path)

    return save_path


async def save_task_zip(bot: Bot, file_id: str, exam_id: str) -> str:
    uuid_value = str(uuid.uuid4())
    filename = f"exam_{exam_id}_task_{uuid_value}.zip"
    save_path = os.path.join(get_tasks_dir(), filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, save_path)
    with zipfile.ZipFile(save_path, 'r') as zipf:
        zipf.extractall('tasks')
    os.remove(save_path)


async def save_task_rar(bot: Bot, file_id: str, exam_id: str) -> str:
    uuid_value = str(uuid.uuid4())
    filename = f"exam_{exam_id}_task_{uuid_value}.rar"
    save_path = os.path.join(get_tasks_dir(), filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, save_path)
