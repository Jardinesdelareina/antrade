from binance.client import Client
import environs
from binance.um_futures import UMFutures

env = environs.Env()
env.read_env('.env')

# Binance API Spot
CLIENT_SPOT = Client(env('API_KEY'), env('SECRET_KEY'), {'verify': True, 'timeout': 20})
ASSET_BALANCE_SPOT = CLIENT_SPOT.get_asset_balance(asset='USDT')
BALANCE_FREE_SPOT = round(float(ASSET_BALANCE_SPOT.get('free')), 1)

# Binance API Futures
CLIENT_FUTURES = UMFutures(env('API_KEY'), env('SECRET_KEY'))
GENERAL_BALANCE = round(float(CLIENT_FUTURES.balance()[7]['balance']), 2)
AVAILABLE_BALANCE = round(float(CLIENT_FUTURES.balance()[7]['availableBalance']), 2)
INFO = CLIENT_FUTURES.exchange_info()
