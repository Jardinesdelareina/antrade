from aiogram.dispatcher.filters.state import StatesGroup, State


class TradeStateGroup(StatesGroup):
    # Состояние параметров: алгоритм, символ, таймфрейм, объем
    algorithms = State()
    symbol = State()
    interval = State()
    qnty = State()
