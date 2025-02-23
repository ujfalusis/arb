import logging
import pickle
import math
from scipy.sparse import csr_array

import numpy as np
from arb.bellmanford import BellmanFord
from arb.router import FromFileToOrderBookRouter
from arb.orderBook import OrderBook


logging.basicConfig(level = logging.DEBUG)

orderbook = OrderBook()
router = FromFileToOrderBookRouter(orderbook)
router.load(50000)

mat = orderbook.matrix
dist, arbitrage, prev = BellmanFord(mat)
orderbook.symbolDict['tBTCUSD'] # 9
orderbook.symbolDict['tETHBTC']
orderbook.symbolDict['tETHUSD']

# USD 1 -> BTC 9 -> ETH 26 -> USD 1

mat[1, 9] + mat[9, 26] + mat[26, 1]
dist[1, 9] + dist[9, 26] + dist[26, 1]


orderbook.assetlist.index('ETH')
orderbook.assetlist[38]
dist[14, 67]

len(orderbook.symbolDict)

'tAUSDTBTC'[1:]

