import io
import requests
from antrade.config_binance import CLIENT
from telegram.config_telegram import CHAT_ID, TELETOKEN

symbol_list = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'DOTUSDT', 'LINKUSDT',
    'ADAUSDT', 'SOLUSDT', 'MATICUSDT', 'UNIUSDT', 'NEARUSDT', 'AVAXUSDT'
]


def round_float(num: float) -> int:
    """ Расчет количества знаков после запятой у числа типа float 
    """
    num_str = str(num)
    counter = 0
    for i in num_str[::-1]:
        if i == '.':
            break
        else:
            counter += 1
    return counter


def get_balance_ticker(ticker) -> float:
    """ Получение баланса спотового кошелька Binance
    """
    asset_balance = CLIENT.get_asset_balance(ticker)
    if ticker == 'USDT':
        round_balance = 1
    else:
        round_balance = 4
    balance_free = round(float(asset_balance.get('free')), round_balance)
    return balance_free


def send_message(message) -> str:
    """ Уведомления в Telegram 
    """
    return requests.get(
        f'https://api.telegram.org/bot{TELETOKEN}/sendMessage', 
        params=dict(chat_id=CHAT_ID, text=message)
    )


def send_report(image_file, message):
    """ Отправка отчета в Telegram 
    """
    with open(image_file, 'rb') as f:
        photo = io.BytesIO(f.read())
    return requests.post(
        f'https://api.telegram.org/bot{TELETOKEN}/sendPhoto',
        data={'chat_id': CHAT_ID, 'caption': message},
        files={'photo': photo}
    )


def report_message(symbol, interval, last_price, stop_loss):
    """ Тектовое сообщение в отчете Telegram
    """
    percentage_diff = round(abs(((last_price - stop_loss) / last_price) * 100), 2)
    return '''{} \n Интервал: {} \n Stop Loss: {} %'''.format(symbol, interval, percentage_diff)


def time_sleep(interval):
    """ Расчет времени ожидания для функции time.sleep()
    """
    _INTERVALS = {'1m': 1, '30m': 30, '1h': 60, '4h': 240, '1d': 1440}
    return 60 * _INTERVALS[interval]
