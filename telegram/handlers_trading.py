from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import asyncio
from .src.config import bot, CHAT_ID, BALANCE_FREE
from .src.algorithms import BotCandles, BotSMA
from .helpers import (
    STATE_ALGO,
    STATE_SYMBOL,
    STATE_INTERVAL,
    STATE_QNTY, 
    STATE_QNTY_TYPE_ERROR,
    STATE_QNTY_VALUE_ERROR,
)
from .keyboards import algorithm_kb, symbol_kb, interval_kb, start_kb, close_kb
from .states import TradeStateGroup

async def get_algorithm(message: types.Message):
    await TradeStateGroup.algorithms.set()
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=STATE_ALGO, 
        parse_mode="HTML", 
        reply_markup=algorithm_kb
    )
    await message.delete()

async def algorithm_callback(callback: types.CallbackQuery, state: FSMContext):
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

        algorithm = data['algorithm']
        symbol = data['symbol']
        interval = data['interval']
        qnty = data['qnty']
        STATE_RESULT = f'Алгоритм: {algorithm} \n Тикер: {symbol} \n Таймфрейм: {interval} \n Объем USDT: {qnty}'
        await TradeStateGroup.next()
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=STATE_RESULT,
            reply_markup=start_kb
        )

async def start_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['start'] = callback.data
        algorithm = data['algorithm']
        STATE_START = f'{algorithm} online'
        await callback.answer(STATE_START)
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=STATE_START,
            reply_markup=close_kb
        )

async def close_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['close'] = callback.data
        

async def stop_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['stop'] = callback.data
        
        await state.finish()

async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await bot.send_message(chat_id=CHAT_ID, text='Отменено')

def register_handlers_trading(dp: Dispatcher):
    dp.register_message_handler(get_algorithm, text='Алгоритмы', state=None)
    dp.register_callback_query_handler(algorithm_callback, state=TradeStateGroup.algorithms)
    dp.register_callback_query_handler(symbol_callback, state=TradeStateGroup.symbol)
    dp.register_callback_query_handler(interval_callback, state=TradeStateGroup.interval)
    dp.register_message_handler(qnty_callback, state=TradeStateGroup.qnty)
    dp.register_callback_query_handler(start_callback, state=TradeStateGroup.start)
    dp.register_callback_query_handler(close_callback, state=TradeStateGroup.close)
    dp.register_callback_query_handler(stop_callback, state=TradeStateGroup.stop)
    dp.register_message_handler(cancel_handler, state="*", text='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state="*")
