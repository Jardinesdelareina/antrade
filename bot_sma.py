from .core import Antrade
import time


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
                elif data.FastSMA.iloc[-1] < data.CloweSMA.iloc[-1] \
                and data.FastSMA.iloc[-1] > data.CloseSMA.iloc[-2]:
                    message = self.symbol + ' Закрыть '
                    self.send_message(message)
                    print(message)
                else:
                    print(f'Open position {self.symbol} {str(self.quantity())}')

            time.sleep(60)

bot = BotSMA('BTCUSDT', '1m', 20)
bot.main()
