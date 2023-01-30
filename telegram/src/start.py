from threading import Thread
from .algorithms import BotSMA, BotTest, BotCandles

""" def btc():
    btc = BotSMA('BTCUSDT', '1m', 20)
    btc.main()

def bnb():
    bnb = BotSMA('BNBUSDT', '1m', 20)
    bnb.main()

thread_btc = Thread(target=btc)
thread_bnb = Thread(target=bnb)
thread_btc.start()
thread_bnb.start() """

test = BotCandles('BTCUSDT', '1m', 20)
test.main()
