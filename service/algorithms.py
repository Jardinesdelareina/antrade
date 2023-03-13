import time
from .core import Antrade

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
        print('Start')
        while online:
            if not self.open_position:
                time.sleep(2)
                print('Покупка')
                self.place_order('BUY')
                break
        if self.open_position:
            while online:
                if closed:
                    print('Ручная продажа')
                    self.place_order('SELL')
                    print('Продано')
                    closed = False
                    break


class SMA(Antrade):
    # Пересечение скользяших средних

    def main(self):
        global online, closed
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
