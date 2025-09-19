import tkinter as tk
import logging
from pprint import pprint

import keys
from connectors.binance_futures import BinanceFuturesClient
from interface.root_component import Root

logger = logging.getLogger()


logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# logger.debug("This message is important only when debugging")
# logger.info("This message shows basic information")
# logger.warning("This message is about something you should pay attention to")
# logger.error("This message helps to debug an error that occured in your program")


if __name__ == '__main__':

    binance_client = BinanceFuturesClient(False, keys.api_public, keys.api_secret)

    root = Root(binance_client)


    root.mainloop()