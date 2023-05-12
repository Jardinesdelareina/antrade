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


def get_balance_spot(ticker) -> float:
    """ Получение баланса спотового кошелька
    """
    asset_balance = CLIENT.get_asset_balance(ticker)
    if ticker == 'USDT':
        round_balance = 1
    else:
        round_balance = 4
    balance_free = round(float(asset_balance.get('free')), round_balance)
    return balance_free


def get_balance_futures_general():
    """ Общий баланс фьючерсного кошелька
    """
    return round(float(CLIENT.futures_account_balance()[8]['balance']), 2)


def get_balance_futures_available():
    """ Свободные средства фьючерсного кошелька
    """
    return round(float(CLIENT.futures_account_balance()[8]['withdrawAvailable']), 2)


def send_message(message) -> str:
    """ Уведомления в Telegram 
    """
    return requests.get(
        f'https://api.telegram.org/bot{TELETOKEN}/sendMessage', 
        params=dict(chat_id=CHAT_ID, text=message)
    )
