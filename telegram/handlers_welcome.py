from aiogram import types, Dispatcher
from .src.config import CHAT_ID, bot
from .helpers import START, DESCRIPTION, BALANCE
from .keyboards import main_kb

# Вызывает главное меню
async def get_start(message: types.Message):
    await bot.send_message(chat_id=CHAT_ID, text=START, parse_mode="HTML", reply_markup=main_kb)
    await message.delete()

# Вызывает описание проекта
async def get_description(message: types.Message):
    await bot.send_message(chat_id=CHAT_ID, text=DESCRIPTION, parse_mode="HTML")
    await message.delete()

# Вызывает информацию о балансе спотового кошелька Binance
async def get_balance(message: types.Message):
    await bot.send_message(chat_id=CHAT_ID, text=BALANCE, parse_mode="HTML")
    await message.delete()

def register_handlers_welcome(dp: Dispatcher):
    dp.register_message_handler(get_start, text='Старт')
    dp.register_message_handler(get_description, text='Описание проекта')
    dp.register_message_handler(get_balance, text='Баланс')
