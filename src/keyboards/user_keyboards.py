from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

user_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Присоединиться к экзамену", callback_data="join_exam")]
])

user_exam_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Готов отвечать", callback_data="student_ready")],
    [InlineKeyboardButton(text="Запросить консультацию", callback_data="request_consultation")]
])