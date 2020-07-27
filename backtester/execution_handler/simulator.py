from typing import Optional
from queue import Queue

from backtester.execution_handler.base import ExecutionHandler
from backtester.event import FillEvent, EventType, OrderEvent
from backtester.price_handler.base import PriceHandler
from backtester.price_parser import PriceParser


class SimulatedStockExecutionHandler(ExecutionHandler):
    """
    The simulated execution handler converts all order objects
    into their equivalent fill objects automatically without latency,
    slippage or fill-ratio issues.

    This allows a straightforward "first go" test of any strategy,
    before implementation with a more sophisticated execution
    handler.
    """

    def __init__(self, events_queue: Queue, price_handler: PriceHandler):
        """
        Initialises the handler, setting the event queue
        as well as access to local pricing.

        :param events_queue:
        :param price_handler:
        """
        self.events_queue = events_queue
        self.price_handler = price_handler

    @staticmethod
    def calculate_commission(quantity: float, fill_price: Optional[float] = 0.0) -> float:
        """
        Calculate the commission for a transaction.
        Fixme: Implement the Quantopian commission algorithm here.
        """
        return min(0.5 * fill_price * quantity, max(1.0, 0.005 * quantity))

    def execute_order(self, event: OrderEvent) -> None:
        """
        Converts OrderEvents into FillEvents "naively",
        without any latency, slippage or fill ratio problems.
        """
        if event.type == EventType.ORDER:
            # Obtain values from the OrderEvent
            timestamp = self.price_handler.get_last_timestamp(event.ticker)
            ticker = event.ticker
            action = event.action
            quantity = event.quantity

            # Obtain the fill price
            if self.price_handler.istick():
                bid, ask = self.price_handler.get_best_bid_ask(ticker)
                if event.action == "BOT":
                    fill_price = ask
                else:
                    fill_price = bid
            else:
                close_price = self.price_handler.get_last_close(ticker)
                fill_price = close_price

            # Set a dummy exchange and calculate trade commission
            exchange = "Oslo Boers"
            commission = SimulatedStockExecutionHandler.calculate_commission(quantity, fill_price)

            # Create the FillEvent and place on the events queue
            fill_event = FillEvent(
                timestamp, ticker,
                action, quantity,
                exchange, fill_price,
                commission
            )
            self.events_queue.put(fill_event)

        return None


class SimulatedFundExecutionHandler(SimulatedStockExecutionHandler):
    """
    Simple override of methods to simulate fund trading.

    Fixme: Include fund commission as a depreciation somehow. Requires metadata.
    Consider to do this in the imput layer instead by adjusting the input prices.
    """

    def __init__(self, events_queue: Queue, price_handler: PriceHandler):
        super().__init__(events_queue=events_queue, price_handler=price_handler)

    @staticmethod
    def calculate_commission(quantity: float, fill_price: Optional[float] = 0.0) -> float:
        """
        Calculate the commission for a transaction.
        """
        return PriceParser.parse(0)
