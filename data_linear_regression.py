from settings import CLIENT
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Получение исторических данных
df = pd.DataFrame(CLIENT.get_historical_klines('BTCUSDT', '4h', '1 Jan, 2014'))
df = df.iloc[:,:5]
df.columns = ['Time', 'Open', 'High', 'Low', 'Close']
df = df.set_index('Time')
df.index = pd.to_datetime(df.index, unit='ms')
df = df.astype(float)

bias = 10

# Создание нового столбца для результатов алгоритма - смещение на размер bias
df['Predict'] = df['Close'].shift(-bias)

X = df[['Close']]
y = df['Predict']

X = X[:-bias]
y = y[:-bias]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = LinearRegression()
model.fit(X_train, y_train)
model_accuracy = model.score(X_test, y_test)
print('Точность модели: ', model_accuracy)

forecast = model.predict(df[['Close']][-bias:])
print('Спрогнозированые данные: ', forecast)

real_data = df['Close'][-bias:]
print('Реальные данные: ', real_data)
