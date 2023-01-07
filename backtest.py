from config import CLIENT
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

symbol = 'XRPUSDT'
interval = '5m'

# Получение исторических данных
df = pd.DataFrame(CLIENT.get_historical_klines(symbol, interval, '1 Dec, 2022', '31 Dec, 2022'))
df = df.iloc[:,:5]
df.columns = ['Time', 'Open', 'High', 'Low', 'Close']
df = df.set_index('Time')
df.index = pd.to_datetime(df.index, unit='ms')
df = df.astype(float)

# Создание SMA и добавление ее значений в таблицу
df['FastSMA'] = df.Close.rolling(window=3).mean()
df['SlowSMA'] = df.Close.rolling(window=100).mean()
df['Buy'] = np.where(
    df.SlowSMA.iloc[-1] < df.FastSMA.iloc[-1] and df.SlowSMA.iloc[-1] >= df.FastSMA.iloc[-2], True, False
)
df['Sell'] = np.where(
    df.SlowSMA.iloc[-1] > df.FastSMA.iloc[-1] and df.SlowSMA.iloc[-1] <= df.FastSMA.iloc[-2], True, False
)
df = df.dropna()

buys = []
sells = []
open_position = False

#Стратегия
for i in range(len(df)):
    if df.FastSMA[i] > df.SlowSMA[i]:
        if open_position == False:
            buys.append(i)
            open_position = True
    if df.FastSMA.iloc[i] < df.SlowSMA[i]:
        if open_position:
            sells.append(i)
            open_position = False

# Создание и описание графика (визуализация)
plt.figure(figsize=(20, 10))
plt.plot(df[['Close', 'FastSMA', 'SlowSMA']])
plt.scatter(df.iloc[buys].index, df.iloc[buys].Close, marker = '^', color = 'g')
plt.scatter(df.iloc[sells].index, df.iloc[sells].Close, marker = 'v', color = 'r')
plt.legend(['Close', 'FastSMA', 'SlowSMA'])
plt.show()

# Математические операции с результатами
merged = pd.concat([df.iloc[buys].Close, df.iloc[sells].Close], axis=1)
merged.columns = ['Buys', 'Sells']
totalprofit = merged.shift(-1).Sells - merged.Buys
result = round(((totalprofit.sum()/df.Close.iloc[-1]) * 100), 2)
print(symbol, str(result) + ' %')
