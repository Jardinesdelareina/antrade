from src.core import Antrade
import time


class BotCandles(Antrade):
    strategy = 'Бычье поглощение'
    
    def main(self, open_position=False):

        while True:
            df = self.get_data()

            # Цена выше/ниже SMA
            trend_bull = df.Cloce.iloc[-1] > df.Hadge.iloc[-1]
            trend_bear = df.Cloce.iloc[-1] < df.Hadge.iloc[-1]

            # Разница между телами свечей
            diff_candles = (df.Close.iloc[-2] + df.Open.iloc[-2]) - (df.Close.iloc[-1] + df.Open.iloc[-1])

            # Тело бычьей свечи закрывает тело медьвежьей больше 60%
            diff_60 = diff_candles < ((df.Close.iloc[-2] + df.Open.iloc[-2]) / 100 * 40)

            # Тело медвежьей свечи закрывает тело бычьей больше 85%
            diff_85 = diff_candles < ((df.Close.iloc[-2] + df.Open.iloc[-2]) / 100 * 15)

            # Бычье поглощение
            bullish_eng = ((df.Close.iloc[-1] > df.Open.iloc[-2]) \
                and (df.Open.iloc[-2] > df.Close.iloc[-2]))

            # Медвежье поглощение
            bearish_eng = ((df.Close.iloc[-1] < df.Open.iloc[-2]) \
                and (df.Open.iloc[-2] > df.Close.iloc[-2]))

            if not open_position:
                if trend_bull & (bullish_eng | diff_60):
                    self.place_order('BUY')
                    open_position = True
                else:
                    print(self.strategy, self.symbol, self.calculate_quantity())

            if open_position:
                if trend_bear & (bearish_eng | diff_85):
                    self.place_order('SELL')
                    open_position = False
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')

            time.sleep(60)

candles = BotCandles('BTCUSDT', '1m', 20)
candles.main()
