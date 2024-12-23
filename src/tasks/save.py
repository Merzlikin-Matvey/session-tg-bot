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


async def rename_files(path,exam_id):
    res = []
    for i in os.listdir(path):
        if 'exam_' not in i:
            uuid_value = str(uuid.uuid4())
            new_name = f"exam_{exam_id}_task_{uuid_value}" + "." + i.split('.')[-1]
            res.append(new_name)
            os.rename(os.path.join(path, i), os.path.join(path, new_name))
    return res

async def move_files(src_folder, dest_folder):
    if not os.path.exists(src_folder):
        raise FileNotFoundError(f"Исходная папка не найдена: {src_folder}")
    
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    for filename in os.listdir(src_folder):
        src_file = os.path.join(src_folder, filename)
        dest_file = os.path.join(dest_folder, filename)
        
        if os.path.isfile(src_file):
            shutil.move(src_file, dest_file)
            print(f"Файл {filename} перемещен в {dest_folder}")

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
    fn = os.listdir('tasks')
    for i in fn:
        if len(i.split('.')) == 1:
            fn = i
            break

    await move_files(f'{get_tasks_dir()}/{fn}', get_tasks_dir())
    os.rmdir(f'{get_tasks_dir()}/{fn}')
    res = await rename_files(get_tasks_dir(), exam_id)
    return res
    


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
        fn = os.listdir('tasks')
        for i in fn:
            if len(i.split('.')) == 1:
                fn = i
                break
        await move_files(f'{get_tasks_dir()}/{fn}', get_tasks_dir())
        os.rmdir(f'{get_tasks_dir()}/{fn}')
        res = await rename_files(get_tasks_dir(), exam_id)
        return res
    except Exception as e:
        print(f"An error occurred during file processing: {e}")
    return ""