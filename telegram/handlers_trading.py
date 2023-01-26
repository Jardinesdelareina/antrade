from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
)
from aiogram import types, Dispatcher
from .src.config import bot, dp
from .helpers import TRADING

async def get_trading(message: types.Message):
    trading_kb = InlineKeyboardMarkup(row_width=2)
    trading_candles = InlineKeyboardButton(text='Бычье поглощение', callback_data='candles')
    trading_sma = InlineKeyboardButton(text='Пересечение SMA', callback_data='sma')
    trading_kb.insert(trading_candles).insert(trading_sma)
    await bot.send_message(chat_id=message.from_user.id, text=TRADING, reply_markup=trading_kb)
    await message.delete()

@dp.callback_query_handler()
async def interface_callback(callback: types.CallbackQuery):
    if callback.data == 'candles':
        await callback.answer('Бычье поглощение online')
    if callback.data == 'sma':
        await callback.answer('Пересечение sma online')

def register_handlers_trading(dp: Dispatcher):
    dp.register_message_handler(get_trading, text='Трейдинг')
    