from fastapi import FastAPI
from src.service import BotCandles, BotSMA

app = FastAPI(
    title='Antrade',
    description='Infrastructure for Algorithmic Trading on Binance',
    version='0.1.0',
)

@app.post("/candles")
def start_candles(symbol: str, interval: str, qnty: int):
    bot = BotCandles(symbol, interval, qnty)
    bot.main()

@app.post("/sma")
def start_sma(symbol: str, interval: str, qnty: int):
    bot = BotSMA(symbol, interval, qnty)
    bot.main()
