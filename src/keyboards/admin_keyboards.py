from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

admin_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Редактировать экзамен", callback_data="edit_exam")],
    [InlineKeyboardButton(text="Создать экзамен", callback_data="add_exam")]
])

admin_task_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Достаточно!")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

admin_back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Главное меню", callback_data="admin_main_menu")]
])
