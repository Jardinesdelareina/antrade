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
                    print(self.strategy, self.symbol, self.quantity())

            if open_position:
                if (data.Close.iloc[-1] < data.Open.iloc[-2] \
                and data.Open.iloc[-2] > data.Close.iloc[-2]) \
                or data.Close.iloc[-1] < data.HadgeSMA.iloc[-1]:
                    self.place_order('SELL')
                    open_position = False
                else:
                    print(f'Open position {self.symbol} {str(self.quantity())}')

            time.sleep(60)

bot = BotCandles('BTCUSDT', '1m', 20)
bot.main()
