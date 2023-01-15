from aiogram import Bot, Dispatcher,executor, types
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
)
from src.config import TELETOKEN, CHAT_ID
from src.telegram.helpers import HELP_COMMAND, DESCRIPTION, START, INTERFACE
from src.service import candles, sma

bot = Bot(TELETOKEN)
dp = Dispatcher(bot)

welcome_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn_help = KeyboardButton('/help')
btn_description = KeyboardButton('/description')
btn_interface = KeyboardButton('/interface')
welcome_kb.insert(btn_help).insert(btn_description).add(btn_interface)

async def on_startup(_):
    print('Online')

@dp.message_handler(commands=['start'])
async def get_start(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=START, 
        parse_mode="HTML",
        reply_markup=welcome_kb
    )
    await message.delete()

@dp.message_handler(commands=['help'])
async def get_help(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=HELP_COMMAND, 
        parse_mode="HTML"
    )
    await message.delete()

@dp.message_handler(commands=['description'])
async def get_description(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=DESCRIPTION, 
        parse_mode="HTML"
    )
    await message.delete()

@dp.message_handler(commands=['interface'])
async def get_interface(message: types.Message):
    ikb = InlineKeyboardMarkup(row_width=2)
    i_candles = InlineKeyboardButton(text='Бычье поглощение', callback_data='candles')
    i_sma = InlineKeyboardButton(text='Пересечение SMA', callback_data='sma')
    ikb.insert(i_candles).insert(i_sma)
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=INTERFACE, 
        reply_markup=ikb
    )
    await message.delete()

@dp.callback_query_handler()
async def interface_callback(callback: types.CallbackQuery):
    if callback.data == 'candles':
        await callback.answer('Бычье поглощение online')
        await candles.main()
    if callback.data == 'sma':
        await callback.answer('Пересечение sma online')
        await sma.main()

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
