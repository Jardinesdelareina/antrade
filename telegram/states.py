from aiogram.dispatcher.filters.state import StatesGroup, State


class TradeStateGroup(StatesGroup):
    # Состояние параметров: алгоритм, символ, таймфрейм, объем, старт алгоритма, остановка алгоритма
    algorithm = State()
    symbol = State()
    interval = State()
    qnty = State()
    start = State()
    stop = State()
