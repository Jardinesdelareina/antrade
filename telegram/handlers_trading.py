from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from .src.config import bot, CHAT_ID, BALANCE_FREE
from .helpers import (
    STATE_ALGO,
    STATE_SYMBOL,
    STATE_INTERVAL,
    STATE_QNTY, 
    STATE_QNTY_TYPE_ERROR,
    STATE_QNTY_VALUE_ERROR,
)
from .keyboards import algorithms_kb, symbol_kb, interval_kb
from .states import TradeStateGroup

async def get_algorithms(message: types.Message):
    await TradeStateGroup.algorithms.set()
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=STATE_ALGO, 
        parse_mode="HTML", 
        reply_markup=algorithms_kb
    )
    await message.delete()

async def algorithms_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['algorithms'] = callback.data
        await TradeStateGroup.next()
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=STATE_SYMBOL, 
        parse_mode="HTML", 
        reply_markup=symbol_kb
    )

async def symbol_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['symbol'] = callback.data
        await TradeStateGroup.next()
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=STATE_INTERVAL, 
            parse_mode="HTML", 
            reply_markup=interval_kb
        )

async def interval_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['interval'] = callback.data
        await TradeStateGroup.next()
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=STATE_QNTY, 
            parse_mode="HTML"
        )

async def qnty_callback(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        quantity = message.text
        try:
            quantity_float = float(quantity)
        except:
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_QNTY_TYPE_ERROR, 
                parse_mode="HTML"
            )
            quantity_float = float(quantity)
        if BALANCE_FREE - quantity_float > 0:
            data['qnty'] = quantity_float
        else:
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_QNTY_VALUE_ERROR, 
                parse_mode="HTML"
            )

    async with state.proxy() as data:
        algorithms = data['algorithms']
        symbol = data['symbol']
        interval = data['interval']
        qnty = data['qnty']
        STATE_RESULT = f'Алгоритм: {algorithms} \n Тикер: {symbol} \n Таймфрейм: {interval} \n Объем USDT: {qnty}'
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=STATE_RESULT
        )
    await state.finish()

async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await bot.send_message(chat_id=CHAT_ID, text='Отменено')

def register_handlers_trading(dp: Dispatcher):
    dp.register_message_handler(get_algorithms, text='Алгоритмы', state=None)
    dp.register_callback_query_handler(algorithms_callback, state=TradeStateGroup.algorithms)
    dp.register_callback_query_handler(symbol_callback, state=TradeStateGroup.symbol)
    dp.register_callback_query_handler(interval_callback, state=TradeStateGroup.interval)
    dp.register_message_handler(qnty_callback, state=TradeStateGroup.qnty)
    dp.register_message_handler(cancel_handler, state="*", text='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state="*")
