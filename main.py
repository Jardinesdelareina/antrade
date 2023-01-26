from aiogram import Bot, Dispatcher,executor, types
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
)
from telegram.src.config import TELETOKEN, CHAT_ID
from telegram.helpers import DESCRIPTION, START, TRADING, HELP, BALANCE

bot = Bot(TELETOKEN)
dp = Dispatcher(bot)

async def on_startup(_):
    print('Online')

@dp.message_handler(commands=['help'])
async def get_description(message: types.Message):
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=HELP, 
        parse_mode="HTML"
    )
    await message.delete()

@dp.message_handler(commands=['description'])
async def get_description(message: types.Message):
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=DESCRIPTION, 
        parse_mode="HTML"
    )
    await message.delete()

@dp.message_handler(commands=['balance'])
async def get_description(message: types.Message):
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=BALANCE, 
        parse_mode="HTML"
    )
    await message.delete()

@dp.message_handler(commands=['start'])
async def main_menu(message: types.Message):
    menu_kb = InlineKeyboardMarkup(row_width=2)
    btn_help = InlineKeyboardButton(text='Команды', callback_data='help')
    btn_description = InlineKeyboardButton(text='Описание проекта', callback_data='description')
    btn_balance = InlineKeyboardButton(text='Баланс', callback_data='balance')
    btn_trading = InlineKeyboardButton(text='Трейдинг', callback_data='trading')
    menu_kb.insert(btn_help).insert(btn_description).insert(btn_balance).add(btn_trading)
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=START, 
        parse_mode="HTML",
        reply_markup=menu_kb
    )
    await message.delete()

@dp.callback_query_handler()
async def menu_callback(callback: types.CallbackQuery):
    if callback.data == 'help':
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=HELP, 
            parse_mode="HTML",
        )
        await callback.answer('Команды')
    if callback.data == 'description':
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=DESCRIPTION, 
            parse_mode="HTML",
        )
        await callback.answer('Описание проекта')
    if callback.data == 'balance':
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=BALANCE, 
            parse_mode="HTML",
        )
        await callback.answer('Баланс')
    if callback.data == 'trading':
        trading_kb = InlineKeyboardMarkup(row_width=2)
        trading_candles = InlineKeyboardButton(text='Бычье поглощение', callback_data='candles')
        trading_sma = InlineKeyboardButton(text='Пересечение SMA', callback_data='sma')
        trading_kb.insert(trading_candles).insert(trading_sma)
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=TRADING, 
            reply_markup=trading_kb
        )
        await callback.answer('Трейдинг')

@dp.callback_query_handler()
async def trading_callback(callback: types.CallbackQuery):
    if callback.data == 'candles':
        await callback.answer('Бычье поглощение online')
        
    if callback.data == 'sma':
        await callback.answer('Пересечение sma online')
        

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
