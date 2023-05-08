from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Меню выбора информера
informer_kb = InlineKeyboardMarkup(row_width=2)
informer_cci = InlineKeyboardButton(text='CCI', callback_data='CCI')
informer_kb.add(informer_cci)

# Меню выбора интервала
interval_kb = InlineKeyboardMarkup(row_width=2)
interval_1m = InlineKeyboardButton(text='1 минута', callback_data='1m')
interval_30m = InlineKeyboardButton(text='30 минут', callback_data='30m')
interval_1h = InlineKeyboardButton(text='1 час', callback_data='1h')
interval_4h = InlineKeyboardButton(text='4 часа', callback_data='4h')
interval_1d = InlineKeyboardButton(text='24 часа', callback_data='1d')
interval_kb.row(interval_1m, interval_30m, interval_1h, interval_4h).insert(interval_1d)
