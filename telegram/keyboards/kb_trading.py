from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Меню выбора алгоритма
algorithm_kb = InlineKeyboardMarkup(row_width=2)
algorithm_test = InlineKeyboardButton(text='Test', callback_data='Test')
algorithm_candles = InlineKeyboardButton(text='Candles', callback_data='Candles')
algorithm_sma = InlineKeyboardButton(text='SMA', callback_data='SMA')
algorithm_kb.add(algorithm_test).add(algorithm_candles).add(algorithm_sma)

# Меню выбора тикера
symbol_kb = InlineKeyboardMarkup(row_width=3)
symbol_btc = InlineKeyboardButton(text='BTC', callback_data='BTCUSDT')
symbol_eth = InlineKeyboardButton(text='ETH', callback_data='ETHUSDT')
symbol_bnb = InlineKeyboardButton(text='BNB', callback_data='BNBUSDT')
symbol_xrp = InlineKeyboardButton(text='XRP', callback_data='XRPUSDT')
symbol_ada = InlineKeyboardButton(text='ADA', callback_data='ADAUSDT')
symbol_dot = InlineKeyboardButton(text='DOT', callback_data='DOTUSDT')
symbol_matic = InlineKeyboardButton(text='MATIC', callback_data='MATICUSDT')
symbol_avax = InlineKeyboardButton(text='AVAX', callback_data='AVAXUSDT')
symbol_trx = InlineKeyboardButton(text='TRX', callback_data='TRXUSDT')
symbol_kb.row(symbol_btc, symbol_eth, symbol_bnb)\
    .row(symbol_xrp, symbol_ada, symbol_dot)\
    .row(symbol_matic, symbol_avax, symbol_trx)

# Меню выбора интервала
interval_kb = InlineKeyboardMarkup(row_width=3)
interval_1m = InlineKeyboardButton(text='1 минута', callback_data='1m')
interval_5m = InlineKeyboardButton(text='5 минут', callback_data='5m')
interval_15m = InlineKeyboardButton(text='15 минут', callback_data='15m')
interval_30m = InlineKeyboardButton(text='30 минут', callback_data='30m')
interval_1h = InlineKeyboardButton(text='1 час', callback_data='1h')
interval_4h = InlineKeyboardButton(text='4 часа', callback_data='4h')
interval_1d = InlineKeyboardButton(text='24 часа', callback_data='1d')
interval_kb.row(interval_1m, interval_5m, interval_15m)\
    .row(interval_30m, interval_1h, interval_4h)\
    .insert(interval_1d)

# Кнопка запуска алгоритма
start_kb = InlineKeyboardMarkup(row_width=1)
start_bot = InlineKeyboardButton(text='Старт', callback_data='start')
start_kb.add(start_bot)
