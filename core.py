from config import CLIENT, CHAT_ID, TELETOKEN
import pandas as pd
import requests, time
from binance.exceptions import BinanceAPIException as bae


class Antrade:

    def __init__(self, symbol, interval, qnty):
        self.symbol = symbol
        self.interval = interval
        self.qnty = qnty

    def get_data(self):
        # Получение данных
        try:
            df = pd.DataFrame(CLIENT.get_historical_klines(self.symbol, self.interval, '1000m UTC'))
        except bae:
            print(bae)
            time.sleep(30)
            df = pd.DataFrame(CLIENT.get_historical_klines(self.symbol, self.interval, '1000m UTC'))
        df = df.iloc[:,:6]
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df = df.set_index('Time')
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.astype(float)
        df['FastSMA'] = df.Close.rolling(window=3).mean()
        df['SlowSMA'] = df.Close.rolling(window=100).mean()
        return df

    def send_message(self, message):
        # Алерт в Telegram
        return requests.get(
            'https://api.telegram.org/bot{}/sendMessage'.format(TELETOKEN), 
            params=dict(chat_id=CHAT_ID, text=message)
        )

    def main(self, open_position=False):
        # Логика

        while True:
            data = self.get_data()
            order_volume = round(self.qnty/data.Close.iloc[-1], 3)

            if not open_position:
                if data.SlowSMA.iloc[-1] < data.FastSMA.iloc[-1] \
                and data.SlowSMA.iloc[-1] >= data.FastSMA.iloc[-2]:
                    order = CLIENT.create_order(symbol=self.symbol, side='BUY', type='MARKET', quantity=order_volume)
                    buyprice = float(order['fills'][0]['price'])
                    message = self.symbol + ' Buy ' + str(buyprice)
                    self.send_message(message)
                    print(message)
                    open_position = True
                else:
                    print(
                        'Ожидание', 
                        self.symbol, 
                        round(data.SlowSMA.iloc[-1], 5), 
                        round(data.FastSMA.iloc[-1], 5),
                    )

            if open_position:
                if data.SlowSMA.iloc[-1] > data.FastSMA.iloc[-1] \
                and data.SlowSMA.iloc[-1] <= data.FastSMA.iloc[-2]:
                    order = CLIENT.create_order(symbol=self.symbol, side='SELL', type='MARKET', quantity=order_volume)
                    sellprice = float(order['fills'][0]['price'])
                    profit = round((sellprice - buyprice) * order_volume)
                    result = f'Результат = {profit}'      
                    message = self.symbol + ' Sell ' + str(result)
                    self.send_message(message)
                    print(message)
                    open_position = False
                else:
                    print(f'Открыта позиция {self.symbol}')

            time.sleep(60)


bot= Antrade('XRPUSDT', '1m', 50)
bot.main()
