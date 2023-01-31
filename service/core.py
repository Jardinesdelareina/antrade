from .config_binance import CLIENT
from telegram.config_telegram import CHAT_ID, TELETOKEN
import pandas as pd
import requests, time, json
from binance.exceptions import BinanceAPIException as bae
from binance.helpers import round_step_size


class Antrade:

    def __init__(self, symbol, interval, qnty, open_position=False):
        self.symbol = symbol
        self.interval = interval
        self.qnty = qnty
        self.open_position = open_position

    def get_data(self):
    # Получение данных
        try:
            df = pd.DataFrame(CLIENT.get_historical_klines(self.symbol, self.interval, '1000m UTC'))
        except:
            print(bae)
            time.sleep(5)
            df = pd.DataFrame(CLIENT.get_historical_klines(self.symbol, self.interval, '1000m UTC'))

        df = df.iloc[:,:6]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df.set_index('Time')
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)
        df['FastSMA'] = df.Close.rolling(window=6).mean()
        df['SlowSMA'] = df.Close.rolling(window=100).mean()
        df['HadgeSMA'] = df.Close.rolling(window=20).mean()
        return df

    def send_message(self, message):
        # Алерт в Telegram
        return requests.get(
            'https://api.telegram.org/bot{}/sendMessage'.format(TELETOKEN), 
            params=dict(chat_id=CHAT_ID, text=message)
        )

    def calculate_quantity(self):
        # Рассчет объема ордера
        symbol_info = CLIENT.get_symbol_info(self.symbol)
        step_size = symbol_info.get('filters')[1]['stepSize']
        df = self.get_data()

        order_volume = self.qnty / df.Close.iloc[-1]
        order_volume = round_step_size(order_volume, step_size)
        return order_volume

    def place_order(self, order_type):
        # Открытие ордера
        if order_type == 'BUY':
            order = CLIENT.create_order(
                symbol=self.symbol, 
                side='BUY', 
                type='MARKET', 
                quantity=self.calculate_quantity(),
            )
            self.open_position = True
            self.buy_price = (order.get('fills')[0]['price'])
            message = f'{self.symbol} \n Buy \n {self.buy_price}'
            self.send_message(message)
            print(message)
            print(json.dumps(order, indent=4, sort_keys=True))

        if order_type == 'SELL':
            order = CLIENT.create_order(
                symbol=self.symbol, 
                side='SELL', 
                type='MARKET', 
                quantity=self.calculate_quantity(),
            )
            self.open_position = False
            sell_price = order.get('fills')[0]['price']
            result = round(((float(sell_price) - float(self.buy_price)) * float(self.calculate_quantity())), 2)
            message = f'{self.symbol} \n Sell \n {sell_price} \n Результат: {result} USDT'
            self.send_message(message)
            print(message)
            print(json.dumps(order, indent=4, sort_keys=True))
