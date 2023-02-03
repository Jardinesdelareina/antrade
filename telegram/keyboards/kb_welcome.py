from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
)

# Главное меню
main_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
main_description = KeyboardButton('Описание проекта')
main_balance = KeyboardButton('Баланс')
main_algorithms = KeyboardButton('Алгоритмы')
main_kb.add(main_description).row(main_balance, main_algorithms)
