from threading import Thread
from .algorithms import BotSMA, BotTest

def btc():
    btc = BotSMA('BTCUSDT', '1m', 20)
    btc.main()

def bnb():
    bnb = BotSMA('BNBUSDT', '1m', 20)
    bnb.main()

thread_btc = Thread(target=btc)
thread_bnb = Thread(target=bnb)
thread_btc.start()
thread_bnb.start()

#test = BotTest('BTCUSDT', '1m', 15)
#test.main()
