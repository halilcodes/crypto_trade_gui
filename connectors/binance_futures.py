import logging
from pprint import pprint

import requests
import time
import keys
import hashlib
import hmac
from urllib.parse import urlencode
import websocket
import threading
import json
import typing
from models import Balance, Candle, Contract, OrderStatus

logger = logging.getLogger()

class BinanceFuturesClient:
    def __init__(self, testnet:bool, api_public: str, api_secret: str):


        if testnet:
            self._base_url = "https://testnet.binancefuture.com"
            self._wss_url = "wss://stream.binancefuture.com/ws"
        else:
            self._base_url = "https://fapi.binance.com"
            # self._base_url = "https://api.binance.com"
            self._wss_url = "wss://fstream.binance.com/ws"


        self._ws_id = 1
        self._ws = None
        self._api_public = api_public
        self._api_secret = api_secret
        self._header = {'X-MBX-APIKEY':self._api_public}


        self.prices = dict()
        self.contracts = self.get_contracts()
        self.balances = self.get_balances()

        self.logs = []


        t = threading.Thread(target=self._start_ws)
        t.start()

        logger.info("Binance Futures Client successfully initialized")

    def _add_log(self, message: str):
        # logger.info("%s", message)
        self.logs.append({"log": message, "displayed": False})


    def _generate_signature(self, data: dict) -> str:

        return hmac.new(self._api_secret.encode(), urlencode(data).encode(),
                        hashlib.sha256).hexdigest()

    def _make_request(self, method: str, endpoint: str, data:typing.Union[None, typing.Dict]=None):

        method = method.upper().strip()
        try:
            if method =="GET":
                response = requests.get(self._base_url + endpoint, params=data, headers=self._header)

            elif method == "POST":
                response = requests.post(self._base_url + endpoint, params=data, headers=self._header)

            elif method == "DELETE":
                response = requests.delete(self._base_url + endpoint, params=data, headers=self._header)

            else:
                raise ValueError("only GET method is allowed for now")

            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error("Connection error while making %s request to %s endpoint: %s",
                         method, endpoint, e)
            return None


        else:
            logger.error("Error while making %s request to %s: %s (error code %s)",
                         method, endpoint, response.json(), response.status_code)
            return None

    def get_contracts(self) -> dict[str, Contract]:
        contracts = dict()

        content = self._make_request("GET", "/fapi/v1/exchangeInfo")
        if content:
            for contract_data in content["symbols"]:
                contracts[contract_data['pair']] = Contract(contract_data)

            return contracts

    def get_historical_candles(self, contract: Contract, interval: str) -> list[Candle]:
        endpoint = "/fapi/v1/klines"
        data = {'symbol': contract.symbol,
                'interval': interval,
                'limit': 1000}
        content = self._make_request("GET", endpoint, data)
        candles = []
        if content:
            for c in content:
                candles.append(Candle(c))
        return candles

    def get_bid_ask(self, contract: Contract) -> dict[str, float]:
        symbol = contract.symbol
        endpoint = "/fapi/v1/ticker/bookTicker"
        data = {'symbol': symbol}
        content = self._make_request("GET", endpoint, data)
        if content:
            if symbol not in self.prices.keys():
                self.prices[symbol] = {'bid': float(content['bidPrice']),
                                       'ask': float(content['askPrice']),
                                       'bidQty': float(content['bidQty']),
                                       'askQty': float(content['askQty'])}
            else:
                self.prices[symbol]['bid'] = float(content['bidPrice'])
                self.prices[symbol]['ask'] = float(content['askPrice'])
            return self.prices[symbol]

    def get_balances(self) -> dict[str, Balance]:
        endpoint = '/fapi/v2/account'

        data = {'timestamp': int(time.time() * 1000)}

        data["signature"] = self._generate_signature(data)

        content = self._make_request("get", endpoint, data)
        balances = dict()

        if content:
            for a in content['assets']:
                balances[a['asset']] = Balance(a)

        return balances

    def place_limit_order(self, contract: Contract, side:str, price:float, quantity:float=1.00,
                          time_in_force:str="GTC") -> typing.Union[OrderStatus, None]:

        endpoint = "/fapi/v1/order"
        symbol = contract.symbol
        data = {
            "symbol": symbol.upper().strip(),
            "side": side.upper().strip(),
            "type": "LIMIT",
            "price": float(price),
            "timeInForce": time_in_force,
            "timestamp": int(time.time() * 1000),
            "quantity": quantity
        }
        data["signature"] = self._generate_signature(data)

        order_status = self._make_request("POST", endpoint, data)

        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def place_market_order(self, contract: Contract, side:str, quantity:float) -> typing.Union[OrderStatus, None]:
        endpoint = "/fapi/v1/order"
        symbol = contract.symbol
        data = {
            "symbol": symbol.upper().strip(),
            "side": side.upper().strip(),
            "type": "MARKET",
            "timestamp": int(time.time() * 1000),
            "quantity": quantity
        }
        data["signature"] = self._generate_signature(data)

        order_status = self._make_request("POST", endpoint, data)

        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def cancel_order(self, contract: Contract, order_id:int) -> typing.Union[OrderStatus, None]:
        endpoint = '/fapi/v1/order'
        symbol = contract.symbol
        data = {'symbol': symbol,
                'orderId': order_id,
                'timestamp': int(time.time() * 1000)
                }

        data["signature"] = self._generate_signature(data)

        order_status = self._make_request("delete", endpoint, data)

        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def get_order_status(self, contract: Contract, order_id) -> typing.Union[OrderStatus, None]:

        endpoint = '/fapi/v1/order'
        symbol = contract.symbol

        data = {'symbol': symbol,
                'orderId': order_id,
                'timestamp': int(time.time() * 1000)
                }

        data["signature"] = self._generate_signature(data)

        order_status = self._make_request("get", endpoint, data)

        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def get_position_info(self, contract: typing.Union[Contract, None]=None):
        endpoint = '/fapi/v3/positionRisk'
        data = {'timestamp': int(time.time() * 1000)}

        if contract:
            data['symbol'] = contract.symbol

        data["signature"] = self._generate_signature(data)
        content = self._make_request("GET", endpoint, data)

        return content

    def _start_ws(self):
        self._ws = websocket.WebSocketApp(self._wss_url, on_open=self._on_open,
                                          on_close=self._on_close, on_error=self._on_error,
                                          on_message=self._on_message)

        while True:
            try:
                self._ws.run_forever()
            except Exception as e:
                logger.error("Binance WSS error in run_forever: %s",e)
            time.sleep(2)

    def _on_open(self, ws):
        logger.info("Websocket Binance Connection opened")
        self.subscribe_channel(list(self.contracts.values()), "bookTicker")

    def _on_close(self, ws, code, msg:str):
        logger.warning("Websocket Binance Connection closed: %s code || %s", code, msg)

    def _on_error(self, ws, msg:str):
        logger.error("Websocket Binance Connection Error: %s", msg)

    def _on_message(self, ws, msg:str):

        data = json.loads(msg)

        if "e" in data:
            if data['e'] == "bookTicker":

                symbol = data['s']

                if symbol not in self.prices:
                    self.prices[symbol] = {'bid': float(data['b']), 'ask': float(data['a']),
                                           'bidQty': float(data['B']),'askQty': float(data['A'])}
                else:
                    self.prices[symbol]['bid'] = float(data['b'])
                    self.prices[symbol]['ask'] = float(data['a'])
                    self.prices[symbol]['bidQty'] = float(data['B'])
                    self.prices[symbol]['askQty'] = float(data['A'])

                #TODO: remove print when done!
                # print(f"{symbol}: {self.prices[symbol]}")
                self._add_log(f"{symbol}: {self.prices[symbol]}")

    def subscribe_channel(self, contracts: list[Contract], channel:str="bookTicker"):
        data = {
        'method': "SUBSCRIBE",
        'params': [],
        }

        for contract in contracts:
            data['params'].append(contract.symbol.lower() + "@"+  channel)

        # data['params'].append("btcusdt@" + channel)
        # data['params'].append("ethusdt@" + channel)
        data['params'].append("adausdt@" + channel)
        # data['params'].append(contracts[0].symbol.lower() + "@" + channel)
        data['id'] =  self._ws_id


        try:
            self._ws.send(json.dumps(data))
        except Exception as e:
            logger.error("Connection error while subbing @ %s: %s",channel, e)

        self._ws_id += 1


if __name__ == "__main__":

    root = Root()

    client = BinanceFuturesClient(root, True, keys.api_public, keys.api_secret)

    root.mainloop()



