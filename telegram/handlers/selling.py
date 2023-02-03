from aiogram import types, Dispatcher
from ..config_telegram import bot, CHAT_ID
from service.core import Antrade

async def selling_handler(message: types.Message):
    if message.text == 'Продать':
        Antrade.place_order(order_type='SELL')
        print('Sell')
        await bot.send_message(
            chat_id=CHAT_ID, 
            text='Ручная продажа'
        )
    else:
        await bot.send_message(
            chat_id=CHAT_ID, 
            text='Простите, команда не распознана'
        )

def register_handlers_selling(dp: Dispatcher):
    dp.register_message_handler(selling_handler, content_types=['text'])
