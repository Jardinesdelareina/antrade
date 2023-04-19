from aiogram import types, Dispatcher
from telegram.config_telegram import CHAT_ID, bot
from telegram.templates import START, DESCRIPTION, HELP, BALANCE
from telegram.keyboards.kb_welcome import main_kb, balance_kb
from antrade.config_binance import CLIENT


async def get_start(message: types.Message):
    """ Главное меню 
    """
    await bot.send_message(chat_id=CHAT_ID, text=START, parse_mode="HTML", reply_markup=main_kb)
    await message.delete()


async def get_description(message: types.Message):
    """ Описание проекта 
    """
    await bot.send_message(chat_id=CHAT_ID, text=DESCRIPTION, parse_mode="HTML")
    await message.delete()


async def get_help(message: types.Message):
    """ Помощь по интерфейсу 
    """
    await bot.send_message(chat_id=CHAT_ID, text=HELP, parse_mode="HTML")
    await message.delete()


async def get_balance(message: types.Message):
    """ Баланс спотового кошелька
    """
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=BALANCE, 
        parse_mode="HTML", 
        reply_markup=balance_kb
    )
    await message.delete()


async def update_balance(callback: types.CallbackQuery):
    """ Обновление баланса
    """
    try:
        if callback.data == 'update':
            CLIENT.get_asset_balance(asset='USDT')
            await callback.answer('Баланс обновлен')
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=BALANCE, 
                parse_mode="HTML", 
                reply_markup=balance_kb
            )
    except:
        BALANCE_EXCEPTION = 'Обновление баланса не удалось'
        await bot.send_message(chat_id=CHAT_ID, text=BALANCE_EXCEPTION, reply_markup=balance_kb)


def register_handlers_welcome(dp: Dispatcher):
    dp.register_message_handler(get_start, text='Старт')
    dp.register_message_handler(get_description, text='О проекте')
    dp.register_message_handler(get_help, text='Помощь')
    dp.register_message_handler(get_balance, text='Баланс')
    dp.register_callback_query_handler(update_balance)
