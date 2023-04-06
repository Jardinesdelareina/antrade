from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
main_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
main_description = KeyboardButton('О проекте')
main_help = KeyboardButton('Помощь')
main_balance = KeyboardButton('Баланс')
main_algorithms = KeyboardButton('Алгоритмы')
main_kb.row(main_description, main_help).row(main_balance, main_algorithms)

# Обновление баланса
balance_kb = InlineKeyboardMarkup(row_width=1)
balance_update = InlineKeyboardButton(text='Обновить', callback_data='update')
balance_kb.row(balance_update)
