from .config_binance import CLIENT
from telegram.config_telegram import CHAT_ID, TELETOKEN
import pandas as pd
import requests, json
from binance.helpers import round_step_size
from .helpers import round_float


class Antrade:

    def __init__(self, symbol, interval, qnty, open_position=False):
        self.symbol = symbol
        self.interval = interval
        self.qnty = qnty
        self.open_position = open_position

    def get_data(self):
    # Получение данных
        df = pd.DataFrame(CLIENT.get_historical_klines(self.symbol, self.interval, '1000m UTC'))
        df = df.iloc[:,:6]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df.set_index('Time')
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)
        return df
    
    def send_message(self, message) -> str:
        # Алерт в Telegram
        return requests.get(
            f'https://api.telegram.org/bot{TELETOKEN}/sendMessage', 
            params=dict(chat_id=CHAT_ID, text=message)
        )

    def last_price(self) -> float:
        # Цена закрытия последней свечи
        df = self.get_data()
        last_price = df.Close.iloc[-1]
        return last_price

    def calculate_quantity(self) -> float:
        # Расчет объема ордера
        symbol_info = CLIENT.get_symbol_info(self.symbol)
        step_size = symbol_info.get('filters')[1]['stepSize']
        order_volume = self.qnty / self.last_price()
        order_volume = round_step_size(order_volume, step_size)
        return order_volume

    def place_order(self, order_type):
        # Размещение ордера

        # Ордер на покупку
        if order_type == 'BUY':
            order = CLIENT.create_order(
                symbol=self.symbol, 
                side='BUY', 
                type='MARKET', 
                quantity=self.calculate_quantity(),
            )
            self.open_position = True
            self.buy_price = round(float(order.get('fills')[0]['price']), round_float(num=self.last_price()))
            message = f'{self.symbol} \n Buy \n {self.buy_price}'
            self.send_message(message)
            print(message)
            print(json.dumps(order, indent=4, sort_keys=True))

            # Stop Loss ордер
            df = self.get_data()
            stop_order = CLIENT.create_order(
                symbol=self.symbol,
                side='SELL',
                type='STOP_LOSS_LIMIT',
                timeInForce='GTC',
                quantity=self.calculate_quantity(),
                stopPrice=df.Low.iloc[-1],
                price=df.Low.iloc[-1],
            )
            print(f'Stop Loss {df.Low.iloc[-1]}')
            print(json.dumps(stop_order, indent=4, sort_keys=True))
            self.stop_loss_order_id = stop_order.get('orderId')
            stop_order_status = CLIENT.get_order(symbol=self.symbol, orderId=self.stop_loss_order_id)
            print(json.dumps(stop_order_status, indent=4, sort_keys=True))
            if stop_order_status.get('status') == 'FILLED':
                self.open_position = False
                message = f'{self.symbol} \n Sell Stop {df.Low.iloc[-1]}'
                self.send_message(message)
                print(message)
                print(json.dumps(stop_order, indent=4, sort_keys=True))

        # Ордер на продажу
        elif order_type == 'SELL':
            order = CLIENT.create_order(
                symbol=self.symbol, 
                side='SELL', 
                type='MARKET', 
                quantity=self.calculate_quantity(),
            )
            self.open_position = False
            self.sell_price = round(float(order.get('fills')[0]['price']), round_float(num=self.last_price()))
            result = round((self.sell_price - self.buy_price * self.calculate_quantity()), 2)
            message = f'{self.symbol} \n Sell \n {self.sell_price} \n Результат: {result} USDT'
            self.send_message(message)
            print(message)
            print(json.dumps(order, indent=4, sort_keys=True))

            # Отмена ордера Stop Loss
            cancel_order = CLIENT.cancel_order(
                symbol=self.symbol,
                orderId=self.stop_loss_order_id
            )
            print(json.dumps(cancel_order, indent=4, sort_keys=True))
            print('Calcel stop loss')
