from config import CLIENT, CHAT_ID, TELETOKEN
import pandas as pd
import requests, time
from binance.exceptions import BinanceAPIException as bae
from symbols import symbols


class Antrade:

    def __init__(self, symbol, interval, qnty):
        self.symbol = symbol
        self.interval = interval
        self.qnty = qnty

    def get_data(self):
        # Получение данных
        df = pd.DataFrame(CLIENT.get_historical_klines(self.symbol, self.interval, '1000m UTC'))
        df = df.iloc[:,:6]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df.set_index('Time')
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)
        df['FastSMA'] = df.Close.rolling(window=3).mean()
        df['SlowSMA'] = df.Close.rolling(window=200).mean()
        return df

    def send_message(self, message):
        # Алерт в Telegram
        return requests.get(
            'https://api.telegram.org/bot{}/sendMessage'.format(TELETOKEN), 
            params=dict(chat_id=CHAT_ID, text=message)
        )

    def main(self, open_position=False):
        # Описание алгоритма
        while True:
            data = self.get_data()
            if not open_position:
                if data.SlowSMA.iloc[-1] < data.FastSMA.iloc[-1] \
                    and data.SlowSMA.iloc[-1] > data.FastSMA.iloc[-2]:
                    order = CLIENT.create_order(symbol=self.symbol, side='BUY', type='MARKET', quantity=self.qnty)
                    buyprice = float(order['fills'][0]['price'])
                    message = self.symbol + ' Buy ' + buyprice
                    self.send_message(message)
                    print(message)
                    open_position = True
                    break
                else:
                    print('Ожидание')
                    time.sleep(60)

        if open_position:
            while True:
                data = self.get_data()
                if data.SlowSMA.iloc[-1] > data.FastSMA.iloc[-1] \
                    and data.SlowSMA.iloc[-1] < data.FastSMA.iloc[-2]:
                    order = CLIENT.create_order(symbol=self.symbol, side='SELL', type='MARKET', quantity=self.qnty)
                    sellprice = float(order['fills'][0]['price'])
                    result = f'Результат = {round((sellprice - buyprice) * self.qnty), 3}'
                    print(result)
                    message = self.symbol + ' Sell ' + result
                    self.send_message(message)
                    print(message)
                    open_position = False
                    break
                else:
                    print('Открыта позиция')
                    time.sleep(60)


bot = Antrade('LTCUSDT', '1m', 20)

bot.main()
