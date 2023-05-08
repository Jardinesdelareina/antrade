import threading
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from telegram.config_telegram import bot, CHAT_ID
from telegram.templates import STATE_INFO, STATE_INTERVAL, STATE_VALID_ERROR, ORDER_EXCEPTION
from telegram.keyboards.kb_informer import informer_kb, interval_kb
from telegram.keyboards.kb_trading import start_kb, stop_kb
from telegram.keyboards.kb_welcome import main_kb
from antrade.informers import start_cci_informer, bot_off


class InformerStateGroup(StatesGroup):
    """ Состояние параметров: информер, таймфрейм, старт/остановка информера
    """
    informer = State()
    interval = State()
    start = State()
    stop = State()


async def get_informers(message: types.Message):
    """ Пункт 'Информеры' главного меню, предлагает список информеров, начинает цикл стейта 
    """
    await InformerStateGroup.informer.set()
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=STATE_INFO, 
        parse_mode="HTML", 
        reply_markup=informer_kb
    )
    await message.delete()


async def cancel_handler(message: types.Message, state: FSMContext):
    """ Отменяет действия, сбрасывает стейт 
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await bot.send_message(chat_id=CHAT_ID, text='Отменено')


async def informer_callback(callback: types.CallbackQuery, state: FSMContext):
    """ Сохраняет информер в стейт, предлагает список информеров 
    """
    async with state.proxy() as data:
        if callback.data in ['CCI']:
            data['informer'] = callback.data
            await InformerStateGroup.next()
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


async def interval_callback(callback: types.CallbackQuery, state: FSMContext):
    """ Сохраняет интервал в стейт, предлагает сверить данные 
    """
    async with state.proxy() as data:
        if callback.data in ['1m', '30m', '1h', '4h', '1d']:
            data['interval'] = callback.data
            await InformerStateGroup.next()
            informer = data['informer']
            interval = data['interval']
            STATE_RESULT = '''Информер: {} \n Таймфрейм: {}'''.format(informer, interval)
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_RESULT,
                reply_markup=start_kb
            )
        else:
            await state.finish()
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_VALID_ERROR,
                parse_mode="HTML",
                reply_markup=main_kb
            )


async def start_callback(callback: types.CallbackQuery, state: FSMContext):
    """ Сохраняет в стейт коллбэк 'start' и запускает информер - вызывается 
        экземпляр определенного информера с параметрами из стейта 
    """
    async with state.proxy() as data:
        try:
            data['start'] = callback.data
            informer = data['informer']
            if data['start'] == 'start':

                if informer == 'CCI':
                    def work():
                        start_cci_informer(data['interval'])
                    thread_work = threading.Thread(target=work)
                    thread_work.start()

                await InformerStateGroup.next()
                STATE_START = f'{informer} начал свою работу'
                await callback.answer(STATE_START)
                await bot.send_message(
                    chat_id=CHAT_ID, 
                    text=STATE_START,
                    reply_markup=ReplyKeyboardRemove()
                )
        except:
            await state.finish()
            print('Ошибка старта')
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=ORDER_EXCEPTION,
                parse_mode="HTML",
                reply_markup=main_kb
            )


async def manage_message(message: types.Message, state: FSMContext):
    """ Остановка работы информера при вводе сообщения 'Стоп' 
    """
    informer = ['informer']
    if message.text == 'Стоп':
        STATE_STOP_MESSAGE = f'\U0001F6D1 Вы действительно хотите остановить {informer}?'
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=STATE_STOP_MESSAGE, 
            reply_markup=stop_kb
        )
        await message.delete()


async def stop_callback(callback: types.CallbackQuery, state: FSMContext):
    """ Коллбэк, обрабатывающий кнопки контрольного вопроса: 
        либо отключает информер, либо продолжает его работу 
    """
    async with state.proxy() as data:
        data['stop'] = callback.data
        informer = data['informer']
        if data['stop'] == 'continue':
            STATE_CONTINUE = f'{informer} продолжает работу' 
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_CONTINUE,
            )
        elif data['stop'] == 'stop':
            bot_off()
            STATE_STOP = f'{informer} закончил свою работу'
            await bot.send_message(
                chat_id=CHAT_ID, 
                text=STATE_STOP, 
                reply_markup=main_kb
            )
            await state.finish()


def register_handlers_informer(dp: Dispatcher):
    dp.register_message_handler(get_informers, text='Информеры', state=None)
    dp.register_message_handler(cancel_handler, state="*", text='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state="*")
    dp.register_callback_query_handler(informer_callback, state=InformerStateGroup.informer)
    dp.register_callback_query_handler(interval_callback, state=InformerStateGroup.interval)
    dp.register_callback_query_handler(start_callback, state=InformerStateGroup.start)
    dp.register_message_handler(manage_message, state="*")
    dp.register_callback_query_handler(stop_callback, state=InformerStateGroup.stop)
