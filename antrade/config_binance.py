from binance.client import Client
import environs

env = environs.Env()
env.read_env('.env')

# Binance API
CLIENT = Client(env('API_KEY'), env('SECRET_KEY'), {'verify': True, 'timeout': 20})

# Futures balance
GENERAL_BALANCE = round(float(CLIENT.futures_account_balance()[8]['balance']), 2)
AVAILABLE_BALANCE = round(float(CLIENT.futures_account_balance()[8]['withdrawAvailable']), 2)
