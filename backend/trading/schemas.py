from pydantic import BaseModel


class GetListOrder(BaseModel):
    # Типизация списка ордеров
    id: int
    order_id: int
    symbol: str
    side: str
    cummulative_quantity: float
    commission: float
    commission_asset: str
    price: float
    status: str
    transaction_time: int
