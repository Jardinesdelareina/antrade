import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Валидные интервалы: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
data = yf.download(tickers='BTC-USD', period='max', interval='1d')

# Отсчет свечей - начальная:конечная
# index - ось X, Close - ось Y
df = data[-365:-1]
plt.plot(df.index, df.Close)

# Plotly выводит результат в браузере на локальном сервере
klines = go.Figure(data=[go.Candlestick(x=df.index,
                                        open=df['Open'],
                                        high=df['High'],
                                        low=df['Low'],
                                        close=df['Close'],
                                        increasing_line_color='green',
                                        decreasing_line_color='red'),

                                        # Горизонтальные линии на графике
                                        go.Scatter(x=df.index, y=[25000]*len(df), line=dict(color='red', width=2), name='Сопротивление'),
                                        go.Scatter(x=df.index, y=[18000]*len(df), line=dict(color='green', width=2), name='Поддержка')])

# Отключает бегунок под графиком
klines.update(layout_xaxis_rangeslider_visible=False)

# Задает цвет фона и размер отступов
klines.update_layout(paper_bgcolor='white',
                        plot_bgcolor='white',
                        margin_l=0, margin_b=0, margin_r=0, margin_t=0)
klines.show()
