from aiogram import types, Dispatcher
from ..config_telegram import bot, CHAT_ID
from service.algorithms import bot_off, bot_close
from ..helpers import *
from ..keyboards.kb_manage import *
from ..keyboards.kb_welcome import *

# Размещение ордера SELL при вводе текстового сообщения 'Продать'
async def selling_message(message: types.Message):
    if message.text == 'Продать':
        try:
            bot_close()
            print('Sell')
            await bot.send_message(
                chat_id=CHAT_ID, 
                text='Ручная продажа'
            )
            await message.delete()
        except:
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=CLOSE_EXCEPTION
            )
            await message.delete()
    """ else:
        await bot.send_message(
            chat_id=CHAT_ID, 
            text='Простите, команда не распознана'
        ) """

# Контрольный вопрос, уточняющий, действительно ли алгоритм нужно отключить
async def stop_message(message: types.Message):
    STATE_STOP_MESSAGE = 'Вы действительно хотите остановить работу алгоритма?'
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=STATE_STOP_MESSAGE, 
        parse_mode="HTML", 
        reply_markup=stop_kb
    )
    await message.delete()

# Коллбэк, обрабатывающий кнопки контрользоно вопроса: либо отключает алгоритм, либо продолжает его работу
async def stop_callback(callback: types.CallbackQuery):
    if callback.data == 'continue':
        await bot.send_message(
            chat_id=CHAT_ID, 
            text='Алгоритм продолжает работу',
            reply_markup=exit_kb
        )
    if callback.data == 'stop':
        bot_off()
        print('Stop')
        await bot.send_message(
            chat_id=CHAT_ID, 
            text='Алгоритм offline', 
            reply_markup=main_kb
        )

def register_handlers_manage(dp: Dispatcher):
    dp.register_message_handler(selling_message, content_types=['text'])
    dp.register_message_handler(stop_message)
    dp.register_callback_query_handler(stop_callback)
