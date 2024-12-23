from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

admin_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Редактировать экзамен", callback_data="edit_exam")],
    [InlineKeyboardButton(text="Создать экзамен", callback_data="add_exam")]
])

admin_edit_exam_keyboard_1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить задание", callback_data="add_task")],
    [InlineKeyboardButton(text="Вступить в экзаменационную комиссию", callback_data="become_teacher")]
])

admin_edit_exam_keyboard_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить задание", callback_data="add_task")],
    [InlineKeyboardButton(text="Покинуть экзаменационную комиссию", callback_data="become_admin")]
])