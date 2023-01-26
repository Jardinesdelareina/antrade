from aiogram import Bot, Dispatcher,executor, types
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,  
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
)
from telegram.src.config import TELETOKEN, CHAT_ID
from telegram.helpers import DESCRIPTION, START, TRADING, BALANCE

bot = Bot(TELETOKEN)
dp = Dispatcher(bot)

async def on_startup(_):
    print('Online')

welcome_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn_description = KeyboardButton('Описание проекта')
btn_balance = KeyboardButton('Баланс')
btn_trading = KeyboardButton('Трейдинг')
welcome_kb.add(btn_description).insert(btn_balance).insert(btn_trading)

@dp.message_handler(text='Старт')
async def get_start(message: types.Message):
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=START, 
        parse_mode="HTML",
        reply_markup=welcome_kb
    )
    await message.delete()

@dp.message_handler(text='Описание проекта')
async def get_description(message: types.Message):
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=DESCRIPTION, 
        parse_mode="HTML"
    )
    await message.delete()

@dp.message_handler(text='Баланс')
async def get_description(message: types.Message):
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=BALANCE, 
        parse_mode="HTML"
    )
    await message.delete()

@dp.message_handler(text='Трейдинг')
async def get_interface(message: types.Message):
    trading_kb = InlineKeyboardMarkup(row_width=2)
    trading_candles = InlineKeyboardButton(text='Бычье поглощение', callback_data='candles')
    trading_sma = InlineKeyboardButton(text='Пересечение SMA', callback_data='sma')
    trading_kb.insert(trading_candles).insert(trading_sma)
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=TRADING, 
        reply_markup=trading_kb
    )
    await message.delete()

@dp.callback_query_handler()
async def interface_callback(callback: types.CallbackQuery):
    if callback.data == 'candles':
        await callback.answer('Бычье поглощение online')
    if callback.data == 'sma':
        await callback.answer('Пересечение sma online')

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
