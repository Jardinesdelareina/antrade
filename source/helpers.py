from binance.helpers import round_step_size
from .config_binance import CLIENT_FUTURES, INFO


def round_float(num: float) -> int:
    """ Расчет количества знаков после запятой у числа типа float """
    num_str = str(num)
    counter = 0
    for i in num_str[::-1]:
        if i == '.':
            break
        else:
            counter += 1
    return counter


def get_min_qnty() -> float:
    """ Информирование о минимальном объеме ордеров по определенной паре """
    last_price = CLIENT_FUTURES.mark_price('BTCUSDT')
    last_price = last_price['markPrice']
    last_price = float(last_price)
    for symbol in INFO['symbols']:
        if symbol['symbol'] == 'BTCUSDT':
            step_size = symbol['filters'][2]['stepSize']
            min_quantity = symbol['filters'][2]['minQty']
            min_quantity = float(min_quantity)
            min_quantity = min_quantity * last_price
            min_quantity = round_step_size(min_quantity, step_size)
            return float(min_quantity)
