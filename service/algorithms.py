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
                time.sleep(5)
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


class Candles(Antrade):
    # Паттерн "Бычье поглощение"

    def main(self):
        global online, closed
        print('Start')

        df = self.get_data()
        df['HadgeSMA'] = df.Close.rolling(window=20).mean()

        # Цена выше/ниже SMA
        trend_bull = df.Close.iloc[-1] > df.HadgeSMA.iloc[-1]
        trend_bear = df.Close.iloc[-1] < df.HadgeSMA.iloc[-1]

        # Бычье поглощение
        bullish_eng = ((df.Close.iloc[-1] > df.Open.iloc[-2]) \
            and (df.Open.iloc[-2] > df.Close.iloc[-2]))

        # Медвежье поглощение
        bearish_eng = ((df.Close.iloc[-1] < df.Open.iloc[-2]) \
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
