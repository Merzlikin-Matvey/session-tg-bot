from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Редактировать экзамены", callback_data="edit_exam")],
    [InlineKeyboardButton(text="Создать экзамен", callback_data="edit_exam")]
])

admin_exam_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="Принять", callback_data="accept_concultation"),
    InlineKeyboardButton(text="Отклонить", callback_data="decline_consultation")
]])
