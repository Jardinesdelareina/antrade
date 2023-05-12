import pandas as pd
import json
from binance.helpers import round_step_size
from antrade.utils import round_float
from antrade.config_binance import CLIENT
from antrade.utils import send_message


class BinanceAPI:
    """ Базовый класс, источник передачи данных через API Binance
    """

    def __init__(self, market, symbol, interval, qnty=50):
        """ Конструктор класса BinanceAPI
            market (str): Тип рынка
            symbol (str): Наименование тикера
            interval (str): Временной интервал
            qnty (float): Размер ордера
            open_position (bool): Состояние, в котором находится алгоритм:
                                если нет открытой позиции, значение атрибута - False,
                                если ордер открыт - True
        """
        self.market = market
        self.symbol = symbol
        self.interval = interval
        self.qnty = qnty
        self.open_position = False

    
    def get_data(self):
        """ Получение данных 
        """
        match self.market:
            case 'spot':
                df = pd.DataFrame(CLIENT.get_historical_klines(
                    symbol=self.symbol, 
                    interval=self.interval, 
                    limit=70
                ))
            case 'futures':
                df = pd.DataFrame(CLIENT.futures_historical_klines(
                    symbol=self.symbol, 
                    interval=self.interval,
                    start_str='1000m UTC'
                ))
        df = df.iloc[:,:5]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close']
        df = df.set_index('Time')
        df.index = pd.to_datetime(df.index, unit='ms')
        return df.astype(float)
    

    def get_last_price(self) -> float:
        """ Вывод цены закрытия последней свечи 
        """
        df = self.get_data()
        return df.Close.iloc[-1]


class Spot(BinanceAPI):
    """ Ордера рынка Spot
    """

    def calculate_quantity(self) -> float:
        """ Расчет объема ордера 
        """
        symbol_info = CLIENT.get_symbol_info(self.symbol)
        step_size = symbol_info.get('filters')[1]['stepSize']
        order_volume = self.qnty / self.get_last_price()
        return round_step_size(order_volume, step_size)


    def place_order(self, order_side: str):
        """ Размещение ордеров

            order_side (str): Направление ордера, передаваемое при вызове функции в алгоритме
        """

        if order_side == 'BUY':
            order = CLIENT.create_order(
                symbol=self.symbol, 
                side='BUY', 
                type='MARKET', 
                quantity=self.calculate_quantity(),
            )
            self.open_position = True
            self.buy_price = round(
                float(order.get('fills')[0]['price']), 
                round_float(num=self.get_last_price())
            )
            message = f'{self.symbol} \n Buy \n {self.buy_price}'
            send_message(message)
            print(message)
            print(json.dumps(order, indent=4, sort_keys=True))

        elif order_side == 'SELL':
            order = CLIENT.create_order(
                symbol=self.symbol, 
                side='SELL', 
                type='MARKET', 
                quantity=self.calculate_quantity(),
            )
            self.open_position = False
            self.sell_price = round(
                float(order.get('fills')[0]['price']), 
                round_float(num=self.get_last_price())
            )
            result = round(((self.sell_price - self.buy_price) * self.calculate_quantity()), 2)
            message = f'{self.symbol} \n Sell \n {self.sell_price} \n Результат: {result} USDT'
            send_message(message)
            print(message)
            print(json.dumps(order, indent=4, sort_keys=True))


class Futures(BinanceAPI):
    """ Ордера рынка Futures
    """

    def calculate_quantity(self) -> float:
        """ Расчет объема ордера 
        """
        INFO = CLIENT.futures_exchange_info()
        for symbol in INFO['symbols']:
            if symbol['symbol'] == self.symbol:
                step_size = symbol['filters'][2]['stepSize']
                return round_step_size((self.qnty / self.get_last_price()), step_size)
            
    
    def place_order(self, order_side: str):
        """ Размещение MARKET ордеров

            order_side (str): Направление ордера, передаваемое при вызове функции в алгоритме
        """
        
        order = CLIENT.futures_create_order(
                symbol=self.symbol, 
                side=order_side, 
                type='MARKET', 
                quantity=self.calculate_quantity(),
        )
        print(f'{self.symbol} {order_side} \n {json.dumps(order, indent=4, sort_keys=True)}')
        message = f'{self.symbol} \n {order_side}: {self.get_last_price()}'
        self.send_message(message)
        