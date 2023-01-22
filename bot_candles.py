from settings import CLIENT, CHAT_ID, TELETOKEN, URL_TELEGRAM
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
        df['HadgeSMA'] = df.Close.rolling(window=50).mean()
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
            message = f'{self.symbol} Sell {self.strategy} {str(sell_price)} Результат: {str(result)}'
            self.send_message(message)
            print(message)
            print(json.dumps(order, indent=4, sort_keys=True))

class BotCandles(Antrade):
    strategy = 'Бычье поглощение'

    def main(self, open_position=False):
        while True:
            df = self.get_data()

            # Цена выше/ниже SMA
            trend_bull = df.Close.iloc[-1] > df.HadgeSMA.iloc[-1]
            trend_bear = df.Close.iloc[-1] < df.HadgeSMA.iloc[-1]

            past_candle_bull = df.Close.iloc[-2] < df.Open.iloc[-2]
            past_candle_bear = df.Close.iloc[-2] < df.Open.iloc[-2]

            # Разница между телами свечей
            diff_candles = (df.Close.iloc[-2] + df.Open.iloc[-2]) - (df.Close.iloc[-1] + df.Open.iloc[-1])

            # Тело бычьей свечи закрывает тело медьвежьей больше 60%
            diff_60 = diff_candles < ((df.Close.iloc[-2] + df.Open.iloc[-2]) / 100 * 40)

            # Тело медвежьей свечи закрывает тело бычьей больше 85%
            diff_85 = diff_candles < ((df.Close.iloc[-2] + df.Open.iloc[-2]) / 100 * 15)

            # Бычье поглощение
            bullish_eng = ((df.Close.iloc[-1] >= df.Open.iloc[-2]) \
                and (df.Open.iloc[-2] > df.Close.iloc[-2]))

            # Медвежье поглощение
            bearish_eng = ((df.Close.iloc[-1] <= df.Open.iloc[-2]) \
                and (df.Open.iloc[-2] < df.Close.iloc[-2]))

            if not open_position:
                if ((past_candle_bull & diff_60) | bullish_eng) & trend_bull:
                    self.place_order('BUY')
                    open_position = True
                else:
                    print(self.strategy, self.symbol, self.calculate_quantity())

            if open_position:
                if ((past_candle_bear & diff_85) | bearish_eng) | trend_bear:
                    self.place_order('SELL')
                    open_position = False
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')

            time.sleep(60)
