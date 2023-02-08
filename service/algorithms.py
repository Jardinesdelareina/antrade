from .core import Antrade
import time

online = True
closed = False

def bot_off():
    global online
    online = False

def bot_closed():
    global closed
    closed = True


class Test(Antrade):

    def main(self):
        global online, closed
        online = True
        closed = False
        print('Start')
        while online:
            if not self.open_position:
                time.sleep(5)
                print('Покупка')
                self.place_order('BUY')
                break
        if self.open_position:
            while online:
                if self.open_position:
                    if closed == True:
                        print('Ручная продажа')
                        self.place_order('SELL')
                        print('Продано')
                        closed = False
                        break


class Candles(Antrade):
    # Паттерн "Бычье поглощение"

    def main(self):
        global online, closed
        online = True
        closed = False
        print('Start')

        df = self.get_data()
        df['HadgeSMA'] = df.Close.rolling(window=20).mean()

        # Цена выше/ниже SMA
        trend_bull = df.Close.iloc[-1] > df.HadgeSMA.iloc[-1]
        trend_bear = df.Close.iloc[-1] < df.HadgeSMA.iloc[-1]

        # Бычье поглощение
        bullish_eng = ((df.Close.iloc[-1] >= df.Open.iloc[-2]) \
            and (df.Open.iloc[-2] > df.Close.iloc[-2]))

        # Медвежье поглощение
        bearish_eng = ((df.Close.iloc[-1] <= df.Open.iloc[-2]) \
            and (df.Open.iloc[-2] < df.Close.iloc[-2]))
            
        while online:
            if not self.open_position:
                if bullish_eng & trend_bull:
                    self.place_order('BUY')
                    break
                else:
                    print(f'{self.symbol} {df.Close.iloc[-1]} Ожидание')
                    time.sleep(60)

        if self.open_position:
            while online:
                if bearish_eng | trend_bear | closed:
                    self.place_order('SELL')
                    break
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')
                    time.sleep(60)


class SMA(Antrade):
    # Пересечение скользяших средних

    def main(self):
        global online, closed
        online = True
        closed = False
        print('Start')

        df = self.get_data()
        df['FastSMA'] = df.Close.rolling(window=6).mean()
        df['SlowSMA'] = df.Close.rolling(window=100).mean()

        trend_bull = (df.FastSMA.iloc[-1] > df.SlowSMA.iloc[-1]) \
            and (df.FastSMA.iloc[-2] < df.SlowSMA.iloc[-2])

        trend_bear = (df.FastSMA.iloc[-1] < df.SlowSMA.iloc[-1]) \
            and (df.FastSMA.iloc[-2] > df.SlowSMA.iloc[-2])

        while online:
            if not self.open_position:
                if trend_bull:
                    self.place_order('BUY')
                    break
                else:
                    print(f'{self.symbol} {df.Close.iloc[-1]} Ожидание')
                    time.sleep(60)

        if self.open_position:
            while online:
                if trend_bear | closed:
                    self.place_order('SELL')
                    break
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')
                    time.sleep(60)


class Woodie(Antrade):
    # Стратегия WoodieCCI

    def cci(self, period) -> float:
        # Расчет индикатора CCI
        df = self.get_data()
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        rolling_mean = typical_price.rolling(window=period).mean()
        rolling_std = typical_price.rolling(window=period).std()
        indicator = round((typical_price - rolling_mean) / (0.015 * rolling_std), 2)
        return indicator

    def main(self):
        global online, closed
        online = True
        closed = False
        print('Start')

        df = self.get_data()
        df['CCI_14'] = self.cci(14)
        df['CCI_6'] = self.cci(6)

        while online:
            if not self.open_position:
                if df.CCI_14.iloc[-1] > 0:
                    print('Покупка')
                    #self.place_order('BUY')
                    break
                else:
                    print(f'{self.symbol} {df.Close.iloc[-1]} Ожидание')
                    time.sleep(60)

        if self.open_position:
            while online:
                if df.CCI_14.iloc[-1] | closed:
                    print('Продажа')
                    #self.place_order('SELL')
                    break
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')
                    time.sleep(60)
