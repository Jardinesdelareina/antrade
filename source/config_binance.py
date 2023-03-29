from binance.client import Client
import environs

env = environs.Env()
env.read_env('.env')

# Binance API
CLIENT_SPOT = Client(env('API_KEY'), env('SECRET_KEY'), {'verify': True, 'timeout': 20})
ASSET_BALANCE = CLIENT_SPOT.get_asset_balance(asset='USDT')
BALANCE_FREE = round(float(ASSET_BALANCE.get('free')), 1)
