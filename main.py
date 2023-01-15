from aiogram import Bot, Dispatcher,executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from src.config import TELETOKEN, CHAT_ID
from src.telegram.helpers import HELP_COMMAND, DESCRIPTION, START

bot = Bot(TELETOKEN)
dp = Dispatcher(bot)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_help = KeyboardButton('/help')
button_description = KeyboardButton('/description')
kb.add(button_help).add(button_description)

@dp.message_handler(commands=['start'])
async def desc_command(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=START, 
        parse_mode="HTML",
        reply_markup=kb
    )
    await message.delete()

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=HELP_COMMAND, 
        parse_mode="HTML"
    )
    await message.delete()

@dp.message_handler(commands=['description'])
async def desc_command(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id, 
        text=DESCRIPTION, 
        parse_mode="HTML"
    )
    await message.delete()

executor.start_polling(dp, skip_updates=True)
