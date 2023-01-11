from src.core import Antrade
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
                    buy_price = float(self.order.get('fills')[0]['price'])
                    message = f'{self.symbol} Buy {self.strategy} {str(buy_price)}'
                    self.send_message(message)
                    print(message)
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
                    sell_price = float(self.order.get('fills')[0]['price'])
                    result = round(((sell_price - buy_price) * self.quantity()), 3)    
                    message = f'{self.symbol} Sell {self.strategy} {str(result)}'
                    self.send_message(message)
                    print(message)
                    open_position = False
                else:
                    print(f'Открыта позиция {self.symbol} {str(self.quantity())}')

            time.sleep(60)

bot = BotSMA('BTCUSDT', '1m', 20)
bot.main()
