from src.config import CLIENT
from tradingview_ta import TA_Handler, Interval
import time

SYMBOL = 'BTCUSDT'
INTERVAL = Interval.INTERVAL_1_MINUTE
QNTY = 50

def get_recommendation():
    # Получение данных от TradingView
    output = TA_Handler(
        symbol=SYMBOL, 
        screener='Crypto', 
        exchange='Binance', 
        interval=INTERVAL
    )

    recommendation = output.get_analysis().summary
    return recommendation

def place_order(order_type):
    # Создание ордера
    order = CLIENT.create_order(symbol=SYMBOL, side=order_type, type='MARKET', quantity=QNTY)
    if order_type == 'BUY' | 'SELL':
        print(order)
        return order

def main():
    # Логика
    buy = False
    sell = True
    while True:
        data = get_recommendation()
        print(data)
        if (data['RECOMMENDATION'] == 'STRONG_BUY' and not buy):
            print('BUY')
            place_order('BUY')
            buy = not buy
            sell = not sell
        if (data['RECOMMENDATION'] == 'STRONG_SELL' and not sell):
            print('SELL')
            place_order('SELL')
            buy = not buy
            sell = not sell
        time.sleep(60)

while True:
    main()
