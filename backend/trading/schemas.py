from pydantic import BaseModel
from datetime import datetime


class GetListOrder(BaseModel):
    # Типизация списка ордеров
    id: int
    order_id: str
    symbol: str
    side: str
    cummulative_quantity: float
    price: float
    status: str
    transaction_time: datetime
