from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    awaiting_full_name = State()
    awaiting_exam_name = State()
    awaiting_exam_datetime = State()
    awaiting_task_image = State()
    awaiting_examiner_number = State()