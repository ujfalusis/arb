import logging
import math
from typing import Dict, List, OrderedDict, Tuple
from bfxapi.websocket.subscriptions import Book
from bfxapi.types import TradingPairBook

from scipy.sparse import csr_array
from sortedcontainers import SortedDict

from arb.bellmanford import BellmanFord

assetcount = 250

def symbolsplitter(symbol: str) -> Tuple[str, str]:
    symbol = symbol[1:] # remove 't' prefix
    return symbol.split(':') if ':' in symbol else (symbol[:3], symbol[3:])

class OrderBook:

    def __init__(self):
        # bid highest price buyer pays, base -> quoted (sell)
        # ask lowest price seller accepts (bid < ask), quoted -> base (buy)
        # {symbol: ([bids{price, amount}], [asks{price, amount}])}
        self.orderbooks: Dict[str, Tuple[Dict[float, float], Dict[float, float]]] = {}
        # {symbol: (index of base asset in csr matrix, index of quoted asset in csr matrix)}
        self.symbolDict: Dict[str, Tuple[int, int]] = {}
        self.assetlist: List = []
        # {(asset1 index, asset2 index) 
        # True - if asset1 is quoted and asset2 is base (asset1(q) -> asset2(b): buy) 
        # False - if reverse (asset1(b) <- asset2(q): sell)}
        self.transitionDict: Dict[Tuple[int, int], bool] = {}
        # graph represents changes costs, row: from asset, column: to asset
        # value:
        # - from asset is base, to asset is quoted -> 1 / bid + fee
        # - from asset is quoted, to asset is base -> ask + fee 
        self.matrix: csr_array = csr_array((assetcount, assetcount), dtype=float)
        self.fee = math.log(1.002)

    def snapshot(self, subscription: Book, snapshot: List[TradingPairBook]):
        symbol = subscription['symbol']
        bids, asks = self.orderbooks.setdefault(symbol, (SortedDict(), SortedDict()))
        if symbol not in self.symbolDict:
            base, quoted = symbolsplitter(symbol)
            assetlist = self.assetlist
            if base not in assetlist:
                assetlist.append(base)
            if quoted not in assetlist:
                assetlist.append(quoted)
            basei, quotedi = assetlist.index(base), assetlist.index(quoted)
            self.symbolDict[symbol] = basei, quotedi
            self.transitionDict[quoted, basei] = True # buy ????
            self.transitionDict[base, quotedi] = False 

        base, quoted = self.symbolDict.get(symbol)

        for bookentry in snapshot:
            # if bookentry.count > 0: # snapshot-nál nem lehet 0
            if bookentry.amount > 0:
                bids[bookentry.price] = bookentry.amount
            else:
                asks[bookentry.price] = -bookentry.amount
        bid, ask = None, None
        if bids:
            bid = bids.iloc[-1]
            self.matrix[base, quoted] = -math.log(bid) + self.fee
        if asks:
            ask = asks.iloc[0]
            self.matrix[quoted, base] = math.log(ask) + self.fee
        
        self._refresh(base, quoted, bid, ask, True)


    def update(self, subscription: Book, data: TradingPairBook):
        symbol = subscription['symbol']
        bids, asks = self.orderbooks[symbol]
        bid, ask = None, None
        base, quoted = self.symbolDict[symbol]
        doRefresh = False
        # logging.debug(f'Update book, symbol: {symbol}, base: {base}, quote: {quote}, data: {data}')
        if data.count > 0:
            if data.amount > 0:
                bidb = bids.iloc[-1] # best bid till now
                bid = data.price # new bid
                bids[bid] = data.amount
                doRefresh = bid > bidb
            else:
                askb = asks.iloc[0] # best ask till now
                ask = data.price # new ask
                asks[ask] = -data.amount
                doRefresh = ask < askb
        else:
            if data.amount == 1:
                del bids[data.price]
                bid = bids.iloc[-1]
                doRefresh = data.price > bid
            else:
                del asks[data.price]
                ask = asks.iloc[0]
                doRefresh = data.price < ask
        if doRefresh:
            self._refresh(base, quoted, bid, ask, False)

    def _refresh(self, base, quoted, bid, ask, snapshot: bool):
        # logging.debug(f'_refresh base: {base}, quoted: {quoted}, bid: {bid}, ask: {ask}, snapshot: {snapshot}')
        if bid:
            # b:BTC -> q:USD: bid
            self.matrix[base, quoted] = -math.log(bid) + self.fee
        if ask:
            # q:USD -> b:BTC: ask
            self.matrix[quoted, base] = math.log(ask) + self.fee
        dist, arb, prev = BellmanFord(self.matrix)
        counts = arb.count(True)
        if counts > 0:
            logging.warning(f'ARBITRAGE {counts}, arb: {arb}, prev: {prev}')




# class OrderBook:
#     def __init__(self):
#         # {symbol, [bids{price, amount}], [asks{price, amount}]}
#         self.orderbooks: Dict[str, Tuple[Dict[float, float], Dict[float, float]]] = {}

#     def init(self, subscription: Book, snapshot: List[TradingPairBook]):
#         symbol = subscription['symbol']
#         bids = OrderedDict()
#         asks = OrderedDict()
#         for bookentry in snapshot:
#             if bookentry.count > 0:
#                 if bookentry.amount > 0:
#                     bids[bookentry.price] = bookentry.amount
#                 else:
#                     asks[bookentry.price] = -bookentry.amount
#         self.orderbooks[symbol] = (bids,  asks)

#     def update(self, subscription: Book, data: TradingPairBook):
#         bids, asks = self.orderbooks[subscription['symbol']]
#         if data.count > 0:
#             if data.amount > 0:
#                 bids[data.price] = data.amount
#             else:
#                 asks[data.price] = -data.amount
#         else:
#             if data.amount == 1:
#                 del bids[data.price]
#             else:
#                 del asks[data.price]
