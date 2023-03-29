from .config_binance import CLIENT_SPOT, CLIENT_FUTURES, INFO
from telegram.config_telegram import CHAT_ID, TELETOKEN
import pandas as pd
import requests, json
from binance.helpers import round_step_size
from .helpers import round_float


class Antrade:
    """ 
    Базовый класс, задающий общие параметры для торговли на спотовом и фьючерсном рынках 
    """

    def __init__(self, symbol, interval, qnty, open_position=False):
        """
        Конструктор класса Antrade. Задает основные параметры, необходимые для взаимодействия
        торговых алгоритмов с биржей.
        
        symbol (str): Наименование тикера
        interval (str): Временной интервал
        qnty (float): Размер ордера
        open_position (bool): Флаг, определяющий состояние позиции, по умолчанию False
        """
        self.symbol = symbol
        self.interval = interval
        self.qnty = qnty
        self.open_position = open_position

    
    def send_message(self, message) -> str:
        """ Уведомления в Telegram """
        return requests.get(
            f'https://api.telegram.org/bot{TELETOKEN}/sendMessage', 
            params=dict(chat_id=CHAT_ID, text=message)
        )


class BinanceAPISpot(Antrade):
    """ 
    Спотовый рынок
    """

    def get_data(self):
        """ Получение данных """
        df = pd.DataFrame(CLIENT_SPOT.get_historical_klines(self.symbol, self.interval, '1000m UTC'))
        df = df.iloc[:,:5]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close']
        df = df.set_index('Time')
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)
        return df


    def get_last_price(self) -> float:
        """ Вывод цены закрытия последней свечи """
        df = self.get_data()
        return df.Close.iloc[-1]


    def calculate_quantity(self) -> float:
        """ Расчет объема ордера """
        symbol_info = CLIENT_SPOT.get_symbol_info(self.symbol)
        step_size = symbol_info.get('filters')[1]['stepSize']
        order_volume = self.qnty / self.last_price()
        order_volume = round_step_size(order_volume, step_size)
        return order_volume


    def place_order(self, order_side: str):
        """
        Размещение ордеров.

        order_side (str): Направление ордера, передаваемое при вызове функции в алгоритме.
        """

        if order_side == 'BUY':
            order = CLIENT_SPOT.create_order(
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

        elif order_side == 'SELL':
            order = CLIENT_SPOT.create_order(
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


class BinanceAPIFutures(Antrade):
    """
    Фьючерсный рынок
    """

    def get_data(self):
        """ Получение данных """
        df = pd.DataFrame(CLIENT_FUTURES.klines(symbol=self.symbol, interval=self.interval, limit=100))
        df = df.iloc[:,:5]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close']
        df = df.set_index('Time')
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)
        return df


    def get_last_price(self) -> float:
        """ Вывод цены закрытия последней свечи """
        df = self.get_data()
        return df.Close.iloc[-1]


    def calculate_quantity(self) -> float:
        """ Расчет объема ордера """
        for symbol in INFO['symbols']:
            if symbol['symbol'] == self.symbol:
                step_size = symbol['filters'][2]['stepSize']
                order_volume = self.qnty / self.get_last_price()
                order_volume = round_step_size(order_volume, step_size)
                return order_volume


    def place_order(self, order_side: str):
        """
        Размещение ордеров.
        
        order_side (string): Тип ордера, передаваемый при вызове функции в алгоритме.
        """
        order = CLIENT_FUTURES.new_order(
            symbol=self.symbol, 
            side=order_side, 
            type='MARKET', 
            quantity=self.calculate_quantity(),
        )
        print(f'{self.symbol} {order_side} \n {json.dumps(order, indent=4, sort_keys=True)}')
        message = f'{self.symbol} \n {order_side}: {self.get_last_price()}'
        self.send_message(message)
        self.open_position = True

        # Уведомление о срабатывании стоп-ордера
        if order_side == 'BUY' and self.open_position:
            if self.get_last_price() <= self.stop_price:
                self.open_position = False
                message = f'{self.symbol} Stop Loss {self.stop_price}'
                self.send_message(message)
        elif order_side == 'SELL' and self.open_position:
            if self.get_last_price() >= self.stop_price:
                self.open_position = False
                message = f'{self.symbol} Stop Loss {self.stop_price}'
                self.send_message(message)


    def place_stop_order(self, order_side: str):
        ''' Размещение стоп-ордера '''
        df = self.get_data()
        if order_side == 'BUY':
            stop_order_side = 'SELL'
            self.stop_price = df.Low.iloc[-1]
        elif order_side == 'SELL':
            stop_order_side = 'BUY'
            self.stop_price = df.High.iloc[-1]

        self.stop_order = CLIENT_FUTURES.new_order(
            symbol=self.symbol, 
            side=stop_order_side, 
            type='STOP_MARKET', 
            stopPrice=self.stop_price,
            quantity=self.calculate_quantity(),
        )
        print(f'Cтоп-ордер \n {json.dumps(self.stop_order, indent=4, sort_keys=True)}')


    def cancel_stop_order(self):
        ''' Отмена ордера '''
        stop_order_id = self.stop_order['orderId']
        orig_client_stop_order_id = self.stop_order['clientOrderId']
        cancel_order = CLIENT_FUTURES.cancel_order(
            symbol=self.symbol,
            orderId=stop_order_id,
            origClientOrderId=orig_client_stop_order_id,
        )
        print(f'''Отмена стоп-ордера
        {json.dumps(cancel_order, indent=4, sort_keys=True)}''')
        self.open_position = False


    def cancel_all_orders(self):
        ''' Отмена всех ордеров '''
        cancel_all_orders = CLIENT_FUTURES.cancel_open_orders(
            symbol=self.symbol,
        )
        print(f'''Отмена всех ордеров по {self.symbol} 
        {json.dumps(cancel_all_orders, indent=4, sort_keys=True)}''')
        self.open_position = False
