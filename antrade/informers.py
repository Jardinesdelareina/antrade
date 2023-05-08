import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from antrade.core import BinanceAPI
from antrade.utils import symbol_list, time_sleep

online = True
closed = False


def bot_off():
    global online
    online = False


class CCIInformer(BinanceAPI):
    """ Система обработки рыночных данных и информирования о ситуациях, 
        которые могут рассматриваться как торговые сигналы:
        1. ZLR
        2. быстрое пересечение индикатором нулевой линии
    """

    def get_cci_values(self, period: int) -> float:
        """ Расчет индикатора CCI 
        
            period (int): Период индикатора, на основании которого производится расчет значений
            return (float): Значение индикатора
        """
        df = self.get_data()
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        rolling_mean = typical_price.rolling(window=period).mean()
        rolling_std = typical_price.rolling(window=period).std()
        indicator = round((typical_price - rolling_mean) / (0.015 * rolling_std), 2)
        return indicator


    def get_report(self):
        """ Создание графического отчета, печать состояния индикатора
        """
        df = self.get_data()

        """ Создание единого пространства для нескольких объектов:
            две строки, одна колонка, общая ось x для двух подграфиков
        """
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

        """ Добавление подграфиков в общее пространство
            1. Японские свечи
            2. Индикатор CCI с периодом 14
            3. Индикатор CCI с периодом 6
        """
        fig.add_trace(go.Candlestick(x=df.index,
                                    open=df['Open'],
                                    high=df['High'],
                                    low=df['Low'],
                                    close=df['Close'],
                                    increasing_line_color='green',
                                    decreasing_line_color='red',
                                    showlegend=False
                                    ),
                                    row=1,
                                    col=1
                                    )
        fig.add_trace(go.Scatter(
                            x=df.index, 
                            y=self.get_cci_values(14),
                            mode='lines', 
                            line=dict(width=2), 
                            marker=dict(color='black'),
                            showlegend=False
                            ), 
                            row=2,
                            col=1
        )
        fig.add_trace(go.Scatter(
                            x=df.index, 
                            y=self.get_cci_values(6),
                            mode='lines', 
                            line=dict(width=1), 
                            marker=dict(color='teal'),
                            showlegend=False
                            ),
                            row=2,
                            col=1
        )

        """ Отклчение бегунка под свечным графиком
        """
        fig.update(layout_xaxis_rangeslider_visible=False)

        """ Настройки общего пространства:
            шкалы измерения графиков справа, фон белый, title пространства - название переменной SYMBOL,
            добавление нулевой линии на подграфик (цвет серый, толщина 1)
        """
        fig.update_layout(
            yaxis=dict(side='right'),
            yaxis2=dict(side='right'),
            paper_bgcolor='white', 
            plot_bgcolor='white', 
            title_text=f'{self.symbol}',
            shapes=[
                dict(
                    type='line', yref='y2', xref='paper',
                    x0=0, y0=0, x1=1, y1=0,
                    line=dict(
                        color='grey',
                        width=1,
                    )
                )
            ]
        )

        """ Запись изображения в формате .png
        """
        fig.write_image(f'{self.symbol}.png')


    def main(self):
        global online
        print('CCI Informer Start')

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

        # Сигналы на продажу
        red_zone = all(cci < 0 for cci in df['CCI_14'][-5:]) or \
            (sum(1 for cci in df['CCI_14'][-5:] if cci > 0) < 5)
        red_zlr = red_zone and (
            (df.CCI_6.iloc[-2] > 0) and \
            (df.CCI_6.iloc[-1] < 0) and \
            (df.CCI_14.iloc[-1] < 0)
        )

        while online:
            if green_zlr or red_zlr:
                self.get_report()
                time.sleep(time_sleep(interval=self.interval))


def start_cci_informer(interval):
    for ticker in symbol_list:
        bot = CCIInformer(symbol=ticker, interval=interval)
        bot.main()
