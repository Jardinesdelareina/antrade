from aiogram import executor
from telegram.src.config import dp
from telegram import handlers_trading, handlers_welcome

async def on_startup(_):
    print('Online')

handlers_welcome.register_handlers_welcome(dp)
handlers_trading.register_handlers_trading(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
