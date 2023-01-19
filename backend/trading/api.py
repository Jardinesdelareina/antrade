from fastapi import APIRouter
from fastapi.responses import JSONResponse
from trading.service.config import BALANCE
from trading.service.strategies import BotCandles

trading_router = APIRouter()

@trading_router.get('/balance')
def get_balance():
    return JSONResponse(BALANCE)

@trading_router.post('/candles')
def get_candles(symbol: str, interval: str, qnty: int):
    candles = BotCandles(symbol, interval, qnty)
    candles.main()

@trading_router.post('/sma')
def get_candles(symbol: str, interval: str, qnty: int):
    sma = BotCandles(symbol, interval, qnty)
    sma.main()
    
