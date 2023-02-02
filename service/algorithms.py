from .core import Antrade
import time

work = True

def bot_off():
    global work
    work = False


class BotTest(Antrade):

    def main(self):
        global work
        work = True
        print('Start')
        while work:
            if not self.open_position:
                time.sleep(5)
                print('Покупка')
                self.place_order('BUY')
            if self.open_position:
                time.sleep(10)
                print('Продажа')
                self.place_order('SELL')

            time.sleep(10)


class BotCandles(Antrade):

    def main(self):
        global work
        work = True
        print('Start')
        while work:
            df = self.get_data()

            # Цена выше/ниже SMA
            trend_bull = df.Close.iloc[-1] > df.HadgeSMA.iloc[-1]
            trend_bear = df.Close.iloc[-1] < df.HadgeSMA.iloc[-1]

            # Бычье поглощение
            bullish_eng = ((df.Close.iloc[-1] >= df.Open.iloc[-2]) \
                and (df.Open.iloc[-2] > df.Close.iloc[-2]))

            # Медвежье поглощение
            bearish_eng = ((df.Close.iloc[-1] <= df.Open.iloc[-2]) \
                and (df.Open.iloc[-2] < df.Close.iloc[-2]))

            if not self.open_position:
                if bullish_eng & trend_bull:
                    self.place_order('BUY')
                else:
                    print(f'{self.symbol} {df.Close.iloc[-1]} Ожидание')

            if self.open_position:
                if bearish_eng | trend_bear:
                    self.place_order('SELL')
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')

            time.sleep(5)



class BotSMA(Antrade):

    def main(self):
        global work
        work = True
        print('Start')
        while work:
            df = self.get_data()

            trend_bull = (df.FastSMA.iloc[-1] > df.SlowSMA.iloc[-1]) \
                and (df.FastSMA.iloc[-2] < df.SlowSMA.iloc[-2])

            trend_bear = (df.FastSMA.iloc[-1] < df.SlowSMA.iloc[-1]) \
                and (df.FastSMA.iloc[-2] > df.SlowSMA.iloc[-2])

            if not self.open_position:
                if trend_bull:
                    self.place_order('BUY')
                else:
                    print(f'{self.symbol} {df.Close.iloc[-1]} Ожидание')

            if self.open_position:
                if trend_bear:
                    self.place_order('SELL')
                else:
                    print(f'Открыта позиция {self.symbol} {self.calculate_quantity()}')

            time.sleep(5)
