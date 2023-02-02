import threading
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import StatesGroup, State
from service.algorithms import BotTest, BotCandles, BotSMA, bot_off
from ..config_telegram import bot, CHAT_ID
from ..helpers import *
from ..keyboards import *


class TradeStateGroup(StatesGroup):
    # Состояние параметров: алгоритм, символ, таймфрейм, объем, старт/остановка алгоритма
    algorithm = State()
    symbol = State()
    interval = State()
    qnty = State()
    start = State()
    stop = State()


# Пункт "Алгоритмы" главного меню, предлагает список алгоритмов, начинает цикл стейта
async def get_algorithm(message: types.Message):
    await TradeStateGroup.algorithm.set()
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=STATE_ALGO, 
        parse_mode="HTML", 
        reply_markup=algorithm_kb
    )
    await message.delete()

# Отменяет действия, сбрасывает стейт
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await bot.send_message(chat_id=CHAT_ID, text='Отменено')

# Сохраняет алгоритм в стейт, предлагает список тикеров
async def algorithm_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback.data in ['Test', 'Candles', 'SMA']:
            data['algorithm'] = callback.data
            await TradeStateGroup.next()
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_SYMBOL, 
                parse_mode="HTML", 
                reply_markup=symbol_kb
            )
        else:
            await state.finish()
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_VALID_ERROR,
                parse_mode="HTML",
                reply_markup=main_kb
            )

# Сохраняет тикер в стейт, предлагает список интервалов
async def symbol_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback.data in [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 
            'XRPUSDT', 'ADAUSDT', 'DOTUSDT', 
            'MATICUSDT', 'AVAUSDT', 'TRXUSDT'
        ]:
            data['symbol'] = callback.data
            await TradeStateGroup.next()
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_INTERVAL, 
                parse_mode="HTML", 
                reply_markup=interval_kb
            )
        else:
            await state.finish()
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_VALID_ERROR,
                parse_mode="HTML",
                reply_markup=main_kb
            )            

# Сохраняет интервал в стейт, предлагает ввести рабочий объем ордеров
async def interval_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if callback.data in ['1m', '5m', '15m', '30m', '1h', '4h', '1d']:
            data['interval'] = callback.data
            await TradeStateGroup.next()
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_QNTY, 
                parse_mode="HTML",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await state.finish()
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_VALID_ERROR,
                parse_mode="HTML",
                reply_markup=main_kb
            )

# Введенный объем проходит валидацию (числовое ли значение и меньше ли баланса),
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
        try:
            data['start'] = callback.data
            if data['start'] == 'start':
                if data['algorithm'] == 'Test':
                    start = BotTest(data['symbol'], data['interval'], data['qnty'])
                elif data['algorithm'] == 'Candles':
                    start = BotCandles(data['symbol'], data['interval'], data['qnty'])
                elif data['algorithm'] == 'SMA':
                    start = BotSMA(data['symbol'], data['interval'], data['qnty'])
                algorithm = data['algorithm']
                STATE_START = f'{algorithm} online'
                await callback.answer(STATE_START)
                await TradeStateGroup.next()
                await bot.send_message(
                    chat_id=CHAT_ID, 
                    text=STATE_START,
                    reply_markup=exit_kb
                )

                def work():
                    start.main()
                thread_work = threading.Thread(target=work)
                thread_work.start()
        except:
            await state.finish()
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=ORDER_EXCEPTION,
                parse_mode="HTML",
                reply_markup=main_kb
            )

async def stop_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        algorithm = data['algorithm']
        STATE_STOP_MESSAGE = f'Вы хотите действительно хотите остановить {algorithm}?'
        await bot.send_message(chat_id=CHAT_ID, text=STATE_STOP_MESSAGE, parse_mode="HTML", reply_markup=stop_kb)
        await message.delete()

async def stop_callback(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['stop'] = callback.data
        if data['stop'] == 'stop':
            bot_off()
            algorithm = data['algorithm']
            STATE_STOP = f'{algorithm} offline'
            print(algorithm, 'Stop')
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_STOP, 
                parse_mode="HTML",
                reply_markup=main_kb
            )
            await state.finish()

def register_handlers_trading(dp: Dispatcher):
    dp.register_message_handler(get_algorithm, text='Алгоритмы', state=None)
    dp.register_message_handler(cancel_handler, state="*", text='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state="*")
    dp.register_callback_query_handler(algorithm_callback, state=TradeStateGroup.algorithm)
    dp.register_callback_query_handler(symbol_callback, state=TradeStateGroup.symbol)
    dp.register_callback_query_handler(interval_callback, state=TradeStateGroup.interval)
    dp.register_message_handler(qnty_message, state=TradeStateGroup.qnty)
    dp.register_callback_query_handler(start_callback, state=TradeStateGroup.start)
    dp.register_message_handler(stop_message, state=TradeStateGroup.stop)
    dp.register_callback_query_handler(stop_callback, state=TradeStateGroup.stop)