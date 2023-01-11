from src.config import CLIENT, CHAT_ID, TELETOKEN
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
            time.sleep(30)
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
            'https://api.telegram.org/bot{}/sendMessage'.format(TELETOKEN), 
            params=dict(chat_id=CHAT_ID, text=message)
        )

    def quantity(self) -> float:
        # Рассчет объема ордера
        symbol_info = CLIENT.get_symbol_info(self.symbol)
        step_size = float(symbol_info.get('filters')[1]['stepSize'])
        data = self.get_data()

        order_volume = self.qnty / data.Close.iloc[-1]
        order_volume = round_step_size(order_volume, step_size)
        return order_volume

    def place_order(self, order_type):
        # Открытие ордера
        if order_type == 'BUY':
            self.order = CLIENT.create_order(symbol=self.symbol, side='BUY', type='MARKET', quantity=self.quantity())
            print(json.dumps(self.order, indent=4, sort_keys=True))
        if order_type == 'SELL':
            self.order = CLIENT.create_order(symbol=self.symbol, side='SELL', type='MARKET', quantity=self.quantity())
            print(json.dumps(self.order, indent=4, sort_keys=True))