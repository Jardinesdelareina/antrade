from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
)

# Меню остановки алгоритма
exit_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
exit_question = KeyboardButton('Остановить алгоритм')
exit_kb.add(exit_question)

# Кнопка остановки алгоритма: да/нет
stop_kb = InlineKeyboardMarkup(row_width=1)
stop_no = InlineKeyboardButton(text='Нет', callback_data='continue')
stop_yes = InlineKeyboardButton(text='Да', callback_data='stop')
stop_kb.row(stop_no, stop_yes)