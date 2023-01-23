from core import Antrade
import time


class BotCandles(Antrade):

    def main(self, open_position=False):
        while True:
            df = self.get_data()

            # Цена выше/ниже SMA
            trend_bull = df.FastSMA.iloc[-1] > df.SlowSMA.iloc[-1]
            trend_bear = df.FastSMA.iloc[-1] < df.SlowSMA.iloc[-1]

            past_candle_bull = df.Close.iloc[-2] > df.Open.iloc[-2]
            past_candle_bear = df.Close.iloc[-2] < df.Open.iloc[-2]

            # Разница между телами свечей
            diff_candles = (df.Close.iloc[-2] + df.Open.iloc[-2]) - (df.Close.iloc[-1] + df.Open.iloc[-1])

            # Тело бычьей свечи закрывает больше 60% тела медьвежьей
            diff_60 = diff_candles < ((df.Close.iloc[-2] + df.Open.iloc[-2]) / 100 * 40)

            # Тело медвежьей свечи закрывает больше 85% тела бычьей
            diff_85 = diff_candles < ((df.Close.iloc[-2] + df.Open.iloc[-2]) / 100 * 15)

            # Бычье поглощение
            bullish_eng = ((df.Close.iloc[-1] >= df.Open.iloc[-2]) \
                and (df.Open.iloc[-2] > df.Close.iloc[-2]))

            # Медвежье поглощение
            bearish_eng = ((df.Close.iloc[-1] <= df.Open.iloc[-2]) \
                and (df.Open.iloc[-2] < df.Close.iloc[-2]))

            if not open_position:
                if ((past_candle_bull & diff_60) | bullish_eng) & trend_bull:
                    self.place_order('BUY')
                    open_position = True
                else:
                    print(f'{self.symbol}  {str(df.Close.iloc[-1])} Нисходящий тренд')

            if open_position:
                if ((past_candle_bear & diff_85) | bearish_eng) | trend_bear:
                    self.place_order('SELL')
                    open_position = False
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')

            time.sleep(60)


start = BotCandles('BTCUSDT', '1m', 20)
start.main()
