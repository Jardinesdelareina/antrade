from core import Antrade
import time


class BotCandles(Antrade):
    # Стратегия: бычье поглощение
    strategy = 'Бычье поглощение'
    
    def main(self, open_position=False):
        while True:
            data = self.get_data()

            if not open_position:
                if (data.Close.iloc[-1] > data.Open.iloc[-2]) \
                and (data.Open.iloc[-2] > data.Close.iloc[-2]):
                    self.place_order('BUY')
                    open_position = True
                else:
                    print(self.strategy, self.symbol, self.calculate_quantity())

            if open_position:
                if (data.Close.iloc[-1] < data.Open.iloc[-2] \
                and data.Open.iloc[-2] > data.Close.iloc[-2]) \
                or data.Close.iloc[-1] < data.HadgeSMA.iloc[-1]:
                    self.place_order('SELL')
                    open_position = False
                else:
                    print(f'Открыта позиция {self.symbol} {str(self.calculate_quantity())}')

            #time.sleep(60)


class BotSMA(Antrade):
    # Стратегия: пересечение скользящих средних
    strategy = 'Пересечение SMA'

    def main(self, open_position=False):
        while True:
            data = self.get_data()

            if not open_position:
                if data.FastSMA.iloc[-1] > data.SlowSMA.iloc[-1] \
                and data.FastSMA.iloc[-1] <= data.SlowSMA.iloc[-2]:
                    self.place_order('BUY')
                    open_position = True
                else:
                    print(
                        self.strategy, 
                        self.symbol,
                        round(data.FastSMA.iloc[-1], 5),
                        round(data.SlowSMA.iloc[-1], 5),
                    )

            if open_position:
                if data.FastSMA.iloc[-1] < data.SlowSMA.iloc[-1] \
                and data.FastSMA.iloc[-1] >= data.SlowSMA.iloc[-2]:
                    self.place_order('SELL')
                    open_position = False
                else:
                    print(f'Открыта позиция {self.symbol} {str(self.calculate_quantity())}')

            time.sleep(60)

candles = BotCandles('XRPUSDT', '1m', 20)
sma = BotSMA('BTCUSDT', '1m', 20)

candles.main()
