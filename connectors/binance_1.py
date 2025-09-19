import logging
import keys
import requests
from pprint import pprint

api_key = keys.api_public
api_secret = keys.api_secret

real_url = "https://fapi.binance.com"
rest_url = "https://testnet.binancefuture.com"
websocket_url = "wss://fstream.binancefuture.com"

logger = logging.getLogger()

def get_contracts():
    contracts = []
    endpoint=  real_url+"/fapi/v1/exchangeInfo"
    response = requests.get(endpoint)
    content = response.json()
    for lot in content["symbols"]:
        contracts.append(lot["pair"])

    return contracts


def get_bid_ask(sym):
    endpoint = real_url+"/fapi/v1/depth"
    params = {"symbol": sym, "limit": 5}
    response = requests.get(endpoint, params=params)
    data = response.json()
    res = {'ask': {'price':data['asks'][0][0], 'qty':data['asks'][0][1]},
           'bid': {'price':data['bids'][0][0], 'qty':data['bids'][0][1]}
           }
    return res
if __name__ == "__main__":
    pprint(get_bid_ask("BTCUSDT"))