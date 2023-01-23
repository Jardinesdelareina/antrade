from src.config import CHAT_ID, TELETOKEN
from dicts.symbols import symbols
import time, requests
from tradingview_ta import TA_Handler, Interval

def get_recommendation(symbol):
    # Получение данных от TradingView
    output = TA_Handler(
        symbol=symbol, 
        screener='Crypto', 
        exchange='Binance', 
        interval=Interval.INTERVAL_1_MINUTE
    )

    recommendation = output.get_analysis().summary
    recommendation['SYMBOL'] = symbol
    return recommendation

def send_message(message):
    # Алерт в Telegram
    return requests.get(
        'https://api.telegram.org/bot{}/sendMessage'.format(TELETOKEN), 
        params=dict(chat_id=CHAT_ID, text=message)
    )  

longs = []
shorts = []

def first_data():
    # Получение первичных данных (не рабочие сигналы)
    print('Поиск данных')
    send_message('Поиск данных')

    # Заполняет списки longs и shorts тикерами с определенными рекомендациями
    for i in symbols:
        data = get_recommendation(i)
        if (data['RECOMMENDATION'] == 'STRONG_BUY'):                
            longs.append(data['SYMBOL'])
        if (data['RECOMMENDATION'] == 'STRONG_SELL'):
            shorts.append(data['SYMBOL'])
        time.sleep(1)
    print('Покупать:')
    print(longs)
    print('Продавать:')
    print(shorts)
    return longs, shorts

first_data()

def work_data():
    # Получение рабочих данных
    for i in symbols:
        data = get_recommendation(i)
        if data['RECOMMENDATION'] == 'STRONG_BUY' and (data['SYMBOL'] not in longs):
            print(data['SYMBOL'], 'Buy')
            message = data['SYMBOL'] + ' Покупать'
            send_message(message)
            longs.append(data['SYMBOL'])
        if data['RECOMMENDATION'] == 'STRONG_SELL' and (data['SYMBOL'] not in shorts):
            print(data['SYMBOL'], 'Sell')
            message = data['SYMBOL'] + ' Продавать'
            send_message(message)
            shorts.append(data['SYMBOL'])
        time.sleep(1)

while True:
    try:
        print('__Новые данные__')
        work_data()
    except:
        time.sleep(60)
        work_data()
