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

"""
{
    "clientOrderId": "3uh8393h843hg943h675",
    "cummulativeQuoteQty": "19.90530000",
    "executedQty": "51.00000000",
    "fills": [
        {
            "commission": "0.00005091",
            "commissionAsset": "BNB",
            "price": "0.39030000",
            "qty": "51.00000000",
            "tradeId": 418576213
        }
    ],
    "orderId": 4963288464,
    "orderListId": -1,
    "origQty": "51.00000000",
    "price": "0.00000000",
    "selfTradePreventionMode": "NONE",
    "side": "SELL",
    "status": "FILLED",
    "symbol": "XRPUSDT",
    "timeInForce": "GTC",
    "transactTime": 1674071772400,
    "type": "MARKET",
    "workingTime": 1674071772400
}
"""