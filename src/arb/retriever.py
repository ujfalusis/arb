import asyncio
import logging
from typing import List
from bfxapi import Client, PUB_WSS_HOST, PUB_REST_HOST
from bfxapi.websocket.subscriptions import Subscription, Book
from bfxapi.types import TradingPairBook

from arb.router import Router, ToFileRouter

logging.basicConfig(level = logging.INFO)

class Retreiver:
    def __init__(self, router: Router) -> None:
        super().__init__()
        bfx = Client(wss_host=PUB_WSS_HOST, rest_host=PUB_REST_HOST)
        self.bfx = bfx

        # pub:list:pair:margin
        # pub:list:pair:futures
        # pub:list:pair:exchange
        pairs = bfx.rest.public.conf('pub:list:pair:exchange')
        pairs = [pair for pair in pairs if 'TEST' not in pair and 'ALT' not in pair and 'HILSV:USD' != pair]
        self.pairs = pairs
        self.router = router

        @bfx.wss.on('open')
        async def on_open() -> None:
            logging.info(f'WSS open.')
            # bfx.wss._websocket.send('{event: "conf", flags: 32768}')
            for symbol in self.pairs:
                await bfx.wss.subscribe('book', symbol = 't' + symbol, prec = 'P0', len = 25)


        @bfx.wss.on('subscribed')
        async def on_subscribed(subscription: Subscription) -> None:
            logging.info(f'WSS subscribed: {subscription}')

        @bfx.wss.on("disconnected")
        async def on_disconnected(code: int, reason: str) -> None:
            logging.warning(f'WSS disconnected, code: {code}, reason: {reason}!')

        @bfx.wss.on("t_book_snapshot")
        def on_t_book_snapshot(subscription: Book, snapshot: List[TradingPairBook]):
            router.snapshot(subscription, snapshot)

        @bfx.wss.on("t_book_update")
        def on_t_book_update(subscription: Book, data: TradingPairBook):
            self.router.update(subscription, data)


async def run():
    router = ToFileRouter()
    try:
        await Retreiver(router).bfx.wss.start()
    finally:
        router.finish()
        logging.info(f'Message routing successfuly finished.')

asyncio.run(
    run()
)

