from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from .src.config import bot, CHAT_ID, BALANCE_FREE
from .src.algorithms import BotTest, BotCandles, BotSMA
from .helpers import (
    STATE_ALGO,
    STATE_SYMBOL,
    STATE_INTERVAL,
    STATE_QNTY, 
    STATE_QNTY_TYPE_ERROR,
    STATE_QNTY_VALUE_ERROR,
)
from .keyboards import algorithm_kb, symbol_kb, interval_kb, start_kb, manage_kb
from .states import TradeStateGroup

# Пункт "Алгоритмы" главного меню, предлагает список алгоритмов
async def get_algorithm(message: types.Message):
    await TradeStateGroup.algorithm.set()
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=STATE_ALGO, 
        parse_mode="HTML", 
        reply_markup=algorithm_kb
    )
    await message.delete()

# Сохраняет алгоритм в стейт, предлагает список тикеров
async def algorithm_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['algorithm'] = callback.data
        await TradeStateGroup.next()
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=STATE_SYMBOL, 
            parse_mode="HTML", 
            reply_markup=symbol_kb
        )

# Сохраняет тикер в стейт, предлагает список интервалов
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

# Сохраняет интервал в стейт, предлагает ввести рабочий объем ордеров
async def interval_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['interval'] = callback.data
        await TradeStateGroup.next()
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=STATE_QNTY, 
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )

# Введенный объем проходит валидацию (числовое ли значение и мельше ли баланса),
# сохраняется в стейт, выводит всю информацию из стейта и предлагает кнопку старта алгоритма
async def qnty_message(message: types.Message, state: FSMContext):
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

# Сохраняет в стейт коллбэк 'start' и запускает алгоритм - в зависимости от параметров
# вызывается экземпляр определенного алгоритма с параметрами из стейта
async def start_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['start'] = callback.data
        if data['start'] == 'start':
            test_start = BotTest(data['symbol'], data['interval'], data['qnty'])
            candles_start = BotCandles(data['symbol'], data['interval'], data['qnty'])
            sma_start = BotSMA(data['symbol'], data['interval'], data['qnty'])
            algorithm = data['algorithm']
            STATE_START = f'{algorithm} online'
            await callback.answer(STATE_START)
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_START,
                reply_markup=manage_kb
            )
            if data['algorithm'] == 'Test':
                await test_start.main(work=True)
            if data['algorithm'] == 'Candles':
                await candles_start.main(work=True)
            if data['algorithm'] == 'SMA':
                await sma_start.main(work=True)
            await TradeStateGroup.next()

# Останавливает цикл алгоритма, сбрасывает стейт и возвращает к списку алгоритмов, где начинается новый стейт
async def stop_message(state: FSMContext):
    async with state.proxy() as data:
        algorithm = data['algorithm']
        STATE_STOP = f'{algorithm} offline'
        test_start = BotTest(data['symbol'], data['interval'], data['qnty'])
        candles_start = BotCandles(data['symbol'], data['interval'], data['qnty'])
        sma_start = BotSMA(data['symbol'], data['interval'], data['qnty'])
        if data['algorithm'] == 'Test':
            await test_start.main(work=False)
        if data['algorithm'] == 'Candles':
            await candles_start.main(work=False)
        if data['algorithm'] == 'SMA':
            await sma_start.main(work=False)
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=STATE_STOP, 
            parse_mode="HTML",
            reply_markup=algorithm_kb
        )
        await state.finish()


# Отменяет действия, сбрасывает стейт
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await bot.send_message(chat_id=CHAT_ID, text='Отменено')

def register_handlers_trading(dp: Dispatcher):
    dp.register_message_handler(get_algorithm, text='Алгоритмы', state=None)
    dp.register_callback_query_handler(algorithm_callback, state=TradeStateGroup.algorithm)
    dp.register_callback_query_handler(symbol_callback, state=TradeStateGroup.symbol)
    dp.register_callback_query_handler(interval_callback, state=TradeStateGroup.interval)
    dp.register_message_handler(qnty_message, state=TradeStateGroup.qnty)
    dp.register_callback_query_handler(start_callback, state=TradeStateGroup.start)
    #dp.register_callback_query_handler(close_callback, state=TradeStateGroup.close)
    dp.register_message_handler(stop_message, state=TradeStateGroup.stop)
    dp.register_message_handler(cancel_handler, state="*", text='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state="*")
