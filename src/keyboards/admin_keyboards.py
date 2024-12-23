from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Присоединиться к экзамену", callback_data="join_exam")],
    [InlineKeyboardButton(text="Все экзамены", callback_data="exam_list")]
])
