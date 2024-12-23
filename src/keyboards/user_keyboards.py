from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

user_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить экзамен", callback_data="add_exam")],
    [InlineKeyboardButton(text="Все экзамены", callback_data="exam_list")]
])
