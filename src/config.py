from binance.client import Client
import environs

env = environs.Env()
env.read_env('.env')

# Binance API
CLIENT = Client(env('API_KEY'), env('SECRET_KEY'), {'verify': True, 'timeout': 20})
BALANCE = CLIENT.get_asset_balance(asset='USDT')

# Telegram API
URL_TELEGRAM = 'https://api.telegram.org/bot{}/sendMessage'
TELETOKEN = env('TELETOKEN')
CHAT_ID = env('CHAT_ID')

# Celery
CELERY_BROKER_URL = env('REDIS')
CELERY_RESULT_BACKEND = env('REDIS')
