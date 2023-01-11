from binance.client import Client
import environs, json

env = environs.Env()
env.read_env('.env')

# Binance API
CLIENT = Client(env('API_KEY'), env('SECRET_KEY'), {'verify': True, 'timeout': 20})
BALANCE = CLIENT.get_asset_balance(asset='USDT')

# Telegram API
TELETOKEN = env('TELETOKEN')
CHAT_ID = env('CHAT_ID')