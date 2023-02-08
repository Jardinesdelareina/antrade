from .core import Antrade
import time

work = True
close = False

def bot_close():
    global close
    close = True

def bot_off():
    global work
    work = False


class BotTest(Antrade):

    def main(self):
        global work, close
        work = True
        close = False
        print('Start')
        while work:
            if not self.open_position:
                time.sleep(5)
                print('Покупка')
                self.place_order('BUY')
            if self.open_position:
                if close == True:
                    print('Ручная продажа')
                    self.place_order('SELL')
                    print('Продано')
                    close = False

            time.sleep(10)

class BotCandles(Antrade):
    # Паттерн "Бычье поглощение"

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
                if bearish_eng | trend_bear | close:
                    self.place_order('SELL')
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')

            time.sleep(60)


class BotSMA(Antrade):
    # Пересечение скользяших средних

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
                if trend_bear | close:
                    self.place_order('SELL')
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')

            time.sleep(60)


class BotWoodie(Antrade):
    # Система WoodieCCI

    # Расчет индикатора 
    def cci(self, period) -> float:
        df = self.get_data()
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        rolling_mean = typical_price.rolling(window=period).mean()
        rolling_std = typical_price.rolling(window=period).std()
        indicator = (typical_price - rolling_mean) / (0.015 * rolling_std)
        return indicator
