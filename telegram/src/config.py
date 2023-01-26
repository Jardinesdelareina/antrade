from binance.client import Client
from aiogram import Bot, Dispatcher

import environs

env = environs.Env()
env.read_env('.env')

# Binance API
CLIENT = Client(env('API_KEY'), env('SECRET_KEY'), {'verify': True, 'timeout': 20})
ASSET_BALANCE = CLIENT.get_asset_balance(asset='USDT')
BALANCE_FREE = round(float(ASSET_BALANCE.get('free')), 1)

# Telegram API
URL_TELEGRAM = 'https://api.telegram.org/bot{}/sendMessage'
TELETOKEN = env('TELETOKEN')
CHAT_ID = env('CHAT_ID')
bot = Bot(TELETOKEN)
dp = Dispatcher(bot)
