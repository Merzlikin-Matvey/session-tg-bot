from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Редактировать экзамены", callback_data="edit_exam")],
    [InlineKeyboardButton(text="Создать экзамен", callback_data="edit_exam")]
])