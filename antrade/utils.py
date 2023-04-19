from .config_binance import CLIENT

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


def get_balance_spot():
    """ Получение баланса спотового кошелька Binance
    """
    asset_balance = CLIENT.get_asset_balance(asset='USDT')
    balance_free = round(float(asset_balance.get('free')), 1)
    return balance_free
