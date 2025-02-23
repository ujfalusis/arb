import logging
import math
import pickle
import numpy as np
from scipy.sparse import csr_array

from arb.bellmanford import BellmanFord
from arb.orderBook import OrderBook
from arb.router import FromFileToOrderBookRouter

logging.basicConfig(level = logging.DEBUG)

orderbook = OrderBook()
router = FromFileToOrderBookRouter(orderbook)
router.load(None)

mat = orderbook.matrix
orderbook.matrix[135, 21]
len(orderbook.assetlist)
math.exp(orderbook.matrix[135, 21] - math.log(1.002))

dist, arbitrage, prev = BellmanFord(mat)

dist[21, 21]
# begin, end = 0, 0
# frm, to = begin, None
# while to != end:

prev[135, 135]
orderbook.assetlist[21] # 21 - BTC
orderbook.assetlist[42] # 42 - ETH
orderbook.assetlist[135] # 135 - XAUT

# ETHBTC - (buy ETH) - ETHXAUT - (sell ETH) - XAUTBTC - (sell XAUT)
orderbook.transitionDict[(21, 42)] # BTC -> ETH, q -> b, buy, legalacsonyabb ask
orderbook.transitionDict[(42, 135)] # ETH -> XAUT, b -> q, sell, legmagasabb bid
orderbook.transitionDict[(135, 21)] # XAUT -> BTC, b -> q, sell, legmagasabb bid
orderbook.symbolDict['tXAUT:BTC']
orderbook.matrix[21, 42] + orderbook.matrix[42, 135] + orderbook.matrix[135, 21]

pr1 = orderbook.orderbooks['tETHBTC'][1].iloc[0]
pr2 = orderbook.orderbooks['tETH:XAUT'][0].iloc[-1]
pr3 = orderbook.orderbooks['tXAUT:BTC'][0].iloc[-1]

math.log(pr1) + math.log(1.002) == orderbook.matrix[21, 42]
-math.log(pr2) + math.log(1.002) == orderbook.matrix[42, 135]
-math.log(pr3) + math.log(1.002) == orderbook.matrix[135, 21]

math.exp(orderbook.matrix[135, 21] - math.log(1.002))

1/pr1*pr2*pr3*pow(1-0.002, 3)

# start = 126
# previ = 126
# lst = []
# while previ != 126 or (previ == 126 and not lst):
#     prevn = orderbook.assetlist[previ]
#     lst.append(prevn + f' - {previ}')
#     previ = prev[start, previ]

# for x in [(126, 125), (125, 124), (124, 126)]:
#     print(x)
#     orderbook.transitionDict[x]

# orderbook.transitionDict[(126, 125)] # USDQ:UST UST -> USDQ, quoted -> base, buy, ask

# orderbook.transitionDict[(125, 124)] # USDQ:USD USDQ -> USD buy, bid
# orderbook.transitionDict[(124, 126)] # sell, ask
# orderbook.symbolDict['tUSDT:USDQ']
# orderbook.transitionDict[(126, 125)]
# mat[126, 125] + mat[125, 124] + mat[124, 126]
# math.exp(mat[126, 125] + mat[125, 124] + mat[124, 126])

# orderbook.assetlist[126] + orderbook.assetlist[42] + orderbook.assetlist[21]
# # 0 - bids, 1 - asks
# (1.0 / orderbook.orderbooks['tETHUST'][1].keys()[0]) * orderbook.orderbooks['tETHBTC'][0].keys()[-1] * orderbook.orderbooks['tBTCUST'][0].keys()[-1] * pow(1-0.002, 3)

# math.log(1.0 / orderbook.orderbooks['tETHUST'][1].keys()[0]) + math.log(orderbook.orderbooks['tETHBTC'][0].keys()[-1]) + math.log(orderbook.orderbooks['tBTCUST'][0].keys()[-1]) - 3 * math.log(1.002)
# math.log(orderbook.orderbooks['tETHUST'][1].keys()[0]) + math.log(1.0 / orderbook.orderbooks['tETHBTC'][0].keys()[-1]) + math.log(1.0 / orderbook.orderbooks['tBTCUST'][0].keys()[-1]) + 3 * math.log(1.002)


# pickle.dump(orderbook, open('data/dummy.pck', 'wb'))

# orderbook: OrderBook = pickle.load(open('data/dummy.pck', 'rb'))
# mat = orderbook.matrix


# retriver started: 20:45
# retriver ended: 20:55
# file size:  220 MB
# load started: 21:00
# events: 3_966_038
# load stopped: 21:35, 30_000 events loaded, no arbitrage
