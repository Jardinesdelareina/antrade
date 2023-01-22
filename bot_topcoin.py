from settings import CLIENT
from binance.exceptions import BinanceAPIException as bae
import pandas as pd
import time

def top_coin():
    # Берет все тикеры, фильтрует их и выводит самый активный
    all_tickers = pd.DataFrame(CLIENT.get_ticker())
    usdt = all_tickers[all_tickers.symbol.str.contains('USDT')]
    work = usdt[~((usdt.symbol.str.contains('UP')) | (usdt.symbol.str.contains('DOWN')))]
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    top_coin = top_coin.symbol.values[0]
    return top_coin

def last_data(symbol, interval, lookback):
    # Принимает и обрабатывает последние исторические данные
    frame = pd.DataFrame(CLIENT.get_historical_klines(symbol, interval, lookback + 'min ago UTC'))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volumes']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

def strategy(qty, SL=0.985, Target=1.02, open_position=False):
    '''     qty - объем ордера
            SL - стоп-лосс 1.5% (число умножается на значение SL)
            Target - тейк-профит 2% (число умножается на значение Target)
    '''

    try:
        # Берет тикер и обрабатывает его последние 120 минутных свечей
        asset = top_coin()
        df = last_data(asset, '1m', '120')
    except:
         # В случае ошибки на стороне сервера делает паузу на 60 секунд и повторяет try
        print(bae)
        time.sleep(60)
        asset = top_coin()
        df = last_data(asset, '1m', '120')

    # Округленный объем ордера
    order_volume = round(qty/df.Close.iloc[-1], 1)

    # Если цена закрытия последней свечи больше, чем предпоследней (если актив растет)...
    if ((df.Close.pct_change() + 1).cumprod()).iloc[-1] > 1:
        print(asset)
        print(df.Close.iloc[-1])
        print(order_volume)

        # Открывает ордер на покупку
        order = CLIENT.create_order(symbol=asset, side='BUY', type='MARKET', quantity=order_volume)
        print(order)

        # Цена открытия ордера
        buyprice = float(order['fills'][0]['price'])

        # Меняет статус позиции на True
        open_position = True

        # Контроль открытой позиции: берет данные за 2 минутные свечи
        while open_position:
            try:
                df = last_data(asset, '1m', '2')
            except bae:
                print(bae)
                print('Restart after 1 min')
                time.sleep(60)
                df = last_data(asset, '1m', '2')

            print(f'Цена ' + str(df.Close[-1]))
            print(f'Цель ' + str(buyprice * Target))
            print(f'Стоп ' + str(buyprice * SL))

            # Если последняя цена <= SL или >= Target...
            if df.Close[-1] <= buyprice * SL or df.Close[-1] >= buyprice * Target:
                
                # Закрывает ордер
                order = CLIENT.create_order(symbol=asset, side='SELL', type='MARKET', quantity=order_volume)
                print(order)
                break

    else:
        print('No find')
        time.sleep(20)

while True:
    # Параметр функции strategy - объем ордера (в USDT)
    strategy(20)
