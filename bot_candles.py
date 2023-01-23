from src.core import Antrade
import time


class BotCandles(Antrade):

    def main(self, open_position=False):
        while True:
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

            if not open_position:
                if bullish_eng & trend_bull:
                    self.place_order('BUY')
                    open_position = True
                else:
                    print(f'{self.symbol} {str(df.Close.iloc[-1])} Ожидание')

            if open_position:
                if bearish_eng | trend_bear:
                    self.place_order('SELL')
                    open_position = False
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')

            time.sleep(60)


start = BotCandles('BTCUSDT', '1m', 20)
start.main()
