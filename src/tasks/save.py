import os
from datetime import datetime
from aiogram import Bot
import yaml
from src.objects.exam import Exam

def get_tasks_dir() -> str:
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    tasks_dir = config['tasks_dir']

    return tasks_dir

async def save_task_image(bot: Bot, file_id: str, exam_id: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"exam_{exam_id}_ticket_{timestamp}.jpg"
    save_path = os.path.join(get_tasks_dir(), filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, save_path)

    return save_path