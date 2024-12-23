from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

user_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Присоединиться к экзамену", callback_data="join_exam")]
])

user_exam_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Готов отвечать")],
    [KeyboardButton(text="Запросить консультацию")]
], resize_keyboard=True)

user_leave_exam_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Покинуть экзамен", callback_data="leave_exam")]
])
