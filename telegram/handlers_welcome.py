from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
)
from aiogram import types, Dispatcher
from .src.config import CHAT_ID, bot
from .helpers import START, DESCRIPTION, BALANCE

welcome_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn_description = KeyboardButton('Описание проекта')
btn_balance = KeyboardButton('Баланс')
btn_trading = KeyboardButton('Трейдинг')
welcome_kb.add(btn_description).insert(btn_balance).insert(btn_trading)

async def get_start(message: types.Message):
    await bot.send_message(chat_id=CHAT_ID, text=START, parse_mode="HTML", reply_markup=welcome_kb)
    await message.delete()

async def get_description(message: types.Message):
    await bot.send_message(chat_id=CHAT_ID, text=DESCRIPTION, parse_mode="HTML")
    await message.delete()

async def get_balance(message: types.Message):
    await bot.send_message(chat_id=CHAT_ID, text=BALANCE, parse_mode="HTML")
    await message.delete()

def register_handlers_welcome(dp: Dispatcher):
    dp.register_message_handler(get_start, text='Старт')
    dp.register_message_handler(get_description, text='Описание проекта')
    dp.register_message_handler(get_balance, text='Баланс')
