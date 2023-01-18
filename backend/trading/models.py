import ormar
from db import MainMeta
from datetime import datetime


class Order(ormar.Model):
    # Модель ордера
    class Meta(MainMeta):
        tablename: str = 'Ордер'

    id: int = ormar.Integer(primary_key=True, autoincrement=True)
    order_id: str = ormar.String(name='Идентификатор', max_length=22, unique=True)
    symbol: str = ormar.String(name='Тикер', max_length=10)
    side: str = ormar.String(name='Направление', max_length=4)
    quantity: float = ormar.Float(name='Объем')
    cummulative_quantity: float = ormar.Float(name='Совокупный объем')
    commission: float = ormar.Float(name='Комиссия')
    commission_asset: str = ormar.String(name='Валюта комиссии', max_length=5)
    price: float = ormar.Float(name='Цена')
    type: str = ormar.String(name='Тип ордера', max_length=50)
    status: str = ormar.String(name='Статус ордера', max_length=20)
    transaction_time: datetime = ormar.DateTime(name='Время ордера', timezone=True, default=datetime.now)
