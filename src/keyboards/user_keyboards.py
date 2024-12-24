from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

user_main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Присоединиться к экзамену", callback_data="join_exam")]
])

user_exam_reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Готов отвечать")],
        [KeyboardButton(text="Запросить консультацию")],
        [KeyboardButton(text="Покинуть экзамен")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

confirm_leave_exam_keyboard_1 = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да, я уверен")],
        [KeyboardButton(text="Нет, я передумал")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

confirm_leave_exam_keyboard_2 = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да, я точно-точно уверен")],
        [KeyboardButton(text="Нет, я все же передумал")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

user_leave_exam_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Покинуть экзамен", callback_data="leave_exam")]
])
