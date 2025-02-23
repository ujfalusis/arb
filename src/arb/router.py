import logging
import pickle
from typing import Dict, List
from bfxapi.websocket.subscriptions import Book
from bfxapi.types import TradingPairBook

from arb.orderBook import OrderBook


class Router:

    def snapshot(self, subscription: Book, snapshot: List[TradingPairBook]):
        pass
    
    def update(self, subscription: Book, data: TradingPairBook):
        pass

    def finish(self):
        pass

class ToFileRouter(Router):
    def __init__(self):
        super().__init__()
        self.events = []

    def snapshot(self, subscription: Book, snapshot: List[TradingPairBook]):
        self.events.append({'type': 'snapshot', 'subscription': subscription, 'snapshot': snapshot})

    def update(self, subscription: Book, data: TradingPairBook):
        self.events.append({'type': 'update', 'subscription': subscription, 'data': data})

    def finish(self):
        pickle.dump(self.events, open('data/data.pck', 'wb'))

class FromFileToOrderBookRouter(Router):
    def __init__(self, orderbook: OrderBook):
        super().__init__()
        self.orderbook = orderbook
        self.events = pickle.load(open('data/data.pck', 'rb'))
        logging.info(f'events len: {len(self.events)}')

    def load(self, limit: int):
        for i, event in enumerate(self.events):
            if event['type'] == 'update':
                self.update(event['subscription'], event['data'])
            elif event['type'] == 'snapshot':
                self.snapshot(event['subscription'], event['snapshot'])
            if i % 10_000 == 0:
                logging.info(f'{i} events loaded')
            if limit and i == limit:
                break
    
    def snapshot(self, subscription: Book, snapshot: List[TradingPairBook]):
        self.orderbook.snapshot(subscription, snapshot)

    def update(self, subscription: Book, data: TradingPairBook):
        self.orderbook.update(subscription, data)
    
