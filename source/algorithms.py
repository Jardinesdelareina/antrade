import time
from .core import BinanceAPISpot, BinanceAPIFutures

online = True
closed = False


def bot_off():
    global online
    online = False


def bot_closed():
    global closed
    closed = True


class Test(BinanceAPISpot):

    def main(self):
        global online, closed
        print('Start')
        while online:
            if not self.open_position:
                time.sleep(2)
                print('Покупка')
                self.place_order('BUY')
                break
        if self.open_position:
            while online:
                if closed:
                    print('Ручная продажа')
                    self.place_order('SELL')
                    print('Продано')
                    closed = False
                    break


class SMA(BinanceAPISpot):
    
    def main(self):
        global online, closed
        print('Start')

        df = self.get_data()
        df['FastSMA'] = df.Close.rolling(window=6).mean()
        df['SlowSMA'] = df.Close.rolling(window=100).mean()

        trend_bull = (df.FastSMA.iloc[-1] > df.SlowSMA.iloc[-1]) \
            and (df.FastSMA.iloc[-2] < df.SlowSMA.iloc[-2])

        trend_bear = (df.FastSMA.iloc[-1] < df.SlowSMA.iloc[-1]) \
            and (df.FastSMA.iloc[-2] > df.SlowSMA.iloc[-2])

        while online:
            if not self.open_position:
                if trend_bull:
                    self.place_order('BUY')
                    break
                else:
                    print(f'{self.symbol} {df.Close.iloc[-1]} Ожидание')
                    time.sleep(60)

        if self.open_position:
            while online:
                if trend_bear | closed:
                    self.place_order('SELL')
                    break
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')
                    time.sleep(60)


class WooCandles(BinanceAPIFutures):

    def get_cci_values(self, period: int) -> float:
        """ 
        Расчет индикатора CCI 
        
        period (int): Период индикатора, на основании которого производится расчет значений
        """
        df = self.get_data()
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        rolling_mean = typical_price.rolling(window=period).mean()
        rolling_std = typical_price.rolling(window=period).std()
        indicator = round((typical_price - rolling_mean) / (0.015 * rolling_std), 2)
        return indicator

    
    def main(self):
        global online, closed
        print('Start')

        df = self.get_data()
        df['CCI_14'] = self.get_cci_values(14)
        df['CCI_6'] = self.get_cci_values(6)

        # Сигналы на покупку
        green_zone = all(cci > 0 for cci in df['CCI_14'][-5:]) or \
            (sum(1 for cci in df['CCI_14'][-5:] if cci < 0) < 5)
        green_zlr = green_zone and (
            (df.CCI_6.iloc[-2] < 0) and \
            (df.CCI_6.iloc[-1] > 0) and \
            (df.CCI_14.iloc[-1] > 0)
        )

        # Покупка: фиксация sell
        green_eng_candles = ((df.Close.iloc[-1] >= df.Open.iloc[-2]) \
            and (df.Open.iloc[-2] > df.Close.iloc[-2]))
        green_double_candles = (df.Close.iloc[-1] < df.Close.iloc[-2]) and \
            (df.Close.iloc[-2] < df.Close.iloc[-3])
        
        # Сигналы на продажу
        red_zone = all(cci < 0 for cci in df['CCI_14'][-5:]) or \
            (sum(1 for cci in df['CCI_14'][-5:] if cci > 0) < 5)
        red_zlr = red_zone and (
            (df.CCI_6.iloc[-2] > 0) and \
            (df.CCI_6.iloc[-1] < 0) and \
            (df.CCI_14.iloc[-1] < 0)
        )

        # Продажа: фиксация buy
        red_eng_candles = ((df.Close.iloc[-1] <= df.Open.iloc[-2]) \
            and (df.Open.iloc[-2] < df.Close.iloc[-2]))
        red_double_candles = (df.Close.iloc[-1] < df.Close.iloc[-2]) and \
            (df.Close.iloc[-2] < df.Close.iloc[-3])
    
        while online:
            if not self.open_position:
                if green_zlr:
                    self.place_order('BUY')
                    self.place_stop_order('BUY')
                    break
                elif red_zlr:
                    self.place_order('SELL')
                    self.place_stop_order('SELL')
                    break
                else:
                    print(f'{self.symbol} {df.Close.iloc[-1]} Ожидание')
                    time.sleep(60)
        if self.open_position:
            while online:
                if green_eng_candles or green_double_candles:
                    self.place_order('SELL')
                    self.cancel_all_orders()
                    break
                elif red_eng_candles or red_double_candles:
                    self.place_order('BUY')
                    self.cancel_all_orders()
                    break
                elif closed:
                    pass
                else:
                    print(f'Открыта позиция {self.symbol} {df.Close.iloc[-1]}')
                    time.sleep(60)
