import hashlib
import hmac
from urllib.parse import urlencode

import time

import keys
import requests

api_key = keys.api_public
api_secret = keys.api_secret
base_url = "https://testnet.binancefuture.com"

endpoint = "/fapi/v1/order"

symbol = "BTCUSDT"
side = "BUY"
type= "LIMIT"
price = 5000.00
timeInForce = "GTC"

headers = {'X-MBX-APIKEY':api_key}

data = {
"symbol": symbol,
"side": side,
"type": type,
"price": price,
"timeInForce": timeInForce,
"timestamp": int(time.time() * 1000),
"quantity": 1
}

signature = hmac.new(api_secret.encode(), urlencode(data).encode(), hashlib.sha256).hexdigest()

data["signature"] = signature

resp = requests.post(base_url+endpoint, data, headers=headers)
print(resp.json())
