import os
import zipfile
import patoolib
import shutil
import aspose.zip as az
from aiogram import Bot
import yaml
import uuid

def get_tasks_dir() -> str:
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    tasks_dir = config['tasks_dir']

    return tasks_dir


async def move_files(source_folder: str, destination_folder: str):
    #попроси копилота
    pass

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
    os.remove(save_path)  # remove the original zip file
    #move_files('tasks/test', 'tasks')
    #os.rmdir('tasks/test')
    #return extract_dir  # Return the base directory
    


async def save_task_rar(bot: Bot, file_id: str, exam_id: str) -> str:
    uuid_value = str(uuid.uuid4())
    filename = f"exam_{exam_id}_task_{uuid_value}.rar"
    save_path = os.path.join(get_tasks_dir(), filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, save_path)

    try:
        extract_dir = get_tasks_dir()
        patoolib.extract_archive(save_path, outdir = extract_dir)
        os.remove(save_path)
        return extract_dir
    except Exception as e:
        print(f"An error occurred during file processing: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        # Attempting to clean up a partially-extracted directory if an error happened
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)  # Remove non-empty directory using shutil
    return ""