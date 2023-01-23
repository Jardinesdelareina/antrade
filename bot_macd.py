from src.config import CLIENT, TELETOKEN, CHAT_ID
from dicts.symbols import symbols
from binance.exceptions import BinanceAPIException as bae
import pandas as pd
import time, ta, requests


class TradeMACD:
    def __init__(self, symbol, interval, qnty):
        self.symbol = symbol
        self.interval = interval
        self.qnty = qnty

    def get_data(self):
        # Получение данных
        df = pd.DataFrame(CLIENT.get_historical_klines(self.symbol, self.interval, '1000m UTC'))
        df = df.iloc[:,:5]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close']
        df = df.set_index('Time')
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)
        return df

    def send_message(self, message):
        # Алерт в Telegram
        return requests.get(
            'https://api.telegram.org/bot{}/sendMessage'.format(TELETOKEN), 
            params=dict(chat_id=CHAT_ID, text=message)
        )

    def place_order(self, order, order_type):
        # Создание ордера
        order = CLIENT.create_order(symbol=self.symbol, side=order_type, type='MARKET', quantity=self.qnty)
        if order_type == 'BUY' | 'SELL':
            print(order)
            return order

    def bot_macd(self, open_position=False):
        title = 'bot_macd' 

        while True:
            data = self.get_data()
            if not open_position:
                if ta.trend.macd_diff(data.Close).iloc[-1] > 0 \
                and ta.trend.macd_diff(data.Close).iloc[-2] < 0:
                    self.place_order(order_type='BUY')
                    buyprice = float(self.order['fills'][0]['price'])
                    message = self.symbol + ' ' + title + ' Buy ' + buyprice + ' ' + str(self.interval)
                    self.send_message(message)
                    print(message)
                    open_position = True
                    break
                else:
                    print('Ожидание ' + title)
                    time.sleep(60)

        if open_position:
            while True:
                data = self.get_data()
                if ta.trend.macd_diff(data.Close).iloc[-1] < 0 \
                and ta.trend.macd_diff(data.Close).iloc[-2] > 0: 
                    self.place_order(order_type='SELL')
                    sellprice = float(self.order['fills'][0]['price'])
                    result = f'Результат = {round((sellprice - buyprice) * self.qnty), 3}'
                    print(result)
                    message = self.symbol + ' ' + title + ' Sell ' + sellprice + ' ' + str(self.interval) + ' ' + result
                    self.send_message(message)
                    print(message)
                    open_position = False
                    break
                else:
                    print('Открыта позиция ' + title)
                    time.sleep(60)

    def start(self):
        try:
            self.bot_macd()
        except bae:
            print(bae)
            time.sleep(60)
            self.bot_macd()


for i in symbols:
    bot = TradeMACD(i, '1m', 50)

bot.start()
