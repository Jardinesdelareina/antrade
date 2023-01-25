from src.core import Antrade
import time


class BotSMA(Antrade):

    def main(self, open_position=False):
        while True:
            df = self.get_data()

            trend_bull = (df.FastSMA.iloc[-1] > df.SlowSMA.iloc[-1]) \
                and (df.FastSMA.iloc[-2] < df.SlowSMA.iloc[-2])

            trend_bear = (df.FastSMA.iloc[-1] < df.SlowSMA.iloc[-1]) \
                and (df.FastSMA.iloc[-2] > df.SlowSMA.iloc[-2])

            if not open_position:
                if trend_bull:
                    self.place_order('BUY')
                    open_position = True
                else:
                    print(self.symbol, df.Close.iloc[-1])

            if open_position:
                if trend_bear:
                    self.place_order('SELL')
                    open_position = False
                else:
                    print(f'Открыта позиция {self.symbol} {str(self.calculate_quantity())}')

            time.sleep(60)
