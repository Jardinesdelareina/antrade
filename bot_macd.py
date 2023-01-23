from src.core import Antrade
import time, ta


class BotMACD(Antrade):

    def main(self, open_position=False):
        while True:
            df = self.get_data()
            if not open_position:
                if ta.trend.macd_diff(df.Close).iloc[-1] > 0 \
                and ta.trend.macd_diff(df.Close).iloc[-2] < 0:
                    self.place_order('BUY')
                    open_position = True
                else:
                    print(f'{self.symbol} {str(df.Close.iloc[-1])} Ожидание')

            if open_position:
                if ta.trend.macd_diff(df.Close).iloc[-1] < 0 \
                and ta.trend.macd_diff(df.Close).iloc[-2] > 0: 
                    self.place_order(order_type='SELL')
                    open_position = False
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')

            time.sleep(60)


start = BotMACD('BTCUSDT', '1m', 50)
start.main()
