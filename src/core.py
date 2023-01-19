from .config import CLIENT, CHAT_ID, TELETOKEN, URL_TELEGRAM
import pandas as pd
import requests, time, json
from binance.exceptions import BinanceAPIException as bae
from binance.helpers import round_step_size


class Antrade:

    def __init__(self, symbol, interval, qnty):
        self.symbol = symbol
        self.interval = interval
        self.qnty = qnty

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
        df['FastSMA'] = df.Close.rolling(window=3).mean()
        df['SlowSMA'] = df.Close.rolling(window=200).mean()
        df['HadgeSMA'] = df.Close.rolling(window=6).mean()
        return df

    def send_message(self, message):
        # Алерт в Telegram
        return requests.get(
            URL_TELEGRAM.format(TELETOKEN), 
            params=dict(chat_id=CHAT_ID, text=message)
        )

    def calculate_quantity(self) -> float:
        # Рассчет объема ордера
        symbol_info = CLIENT.get_symbol_info(self.symbol)
        step_size = float(symbol_info.get('filters')[1]['stepSize'])
        data = self.get_data()

        order_volume = self.qnty / data.Close.iloc[-1]
        order_volume = round_step_size(order_volume, step_size)
        print(order_volume)
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
            self.buy_price = float(order.get('fills')[0]['price'])
            message = f'{self.symbol} Buy {self.strategy} {str(self.buy_price)}'
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
            sell_price = float(order.get('fills')[0]['price'])
            result = round(((sell_price - self.buy_price) * self.calculate_quantity()), 3)    
            message = f'{self.symbol} Sell {self.strategy} {str(result)}'
            self.send_message(message)
            print(message)
            print(json.dumps(order, indent=4, sort_keys=True))
