from fastapi import APIRouter
from typing import List
from .schemas import GetListOrder
from .models import Order

trading_router = APIRouter()

@trading_router.get('/orders', response_model=List[GetListOrder])
async def get_list_order():
    return await Order.objects.all()
