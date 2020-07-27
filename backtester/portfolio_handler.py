from queue import Queue

from backtester.portfolio import Portfolio
from backtester.price_handler.base import PriceHandler
from backtester.event import OrderEvent, FillEvent


class PortfolioHandler(object):
    def __init__(self, initial_cash: float, events_queue: Queue, price_handler: PriceHandler):
        """
        The PortfolioHandler is designed to interact with the
        backtesting or live trading overall event-driven
        architecture. It exposes two methods, on_signal and
        on_fill, which handle how SignalEvent and FillEvent
        objects are dealt with.

        Each PortfolioHandler contains a Portfolio object,
        which stores the actual Position objects.

        The PortfolioHandler takes a handle to a PositionSizer
        object which determines a mechanism, based on the current
        Portfolio, as to how to size a new Order.

        The PortfolioHandler also takes a handle to the
        RiskManager, which is used to modify any generated
        Orders to remain in line with risk parameters.
        """
        self.initial_cash = initial_cash
        self.events_queue = events_queue
        self.price_handler = price_handler
        self.portfolio = Portfolio(price_handler=price_handler, cash=initial_cash)

    def _convert_fill_to_portfolio_update(self, fill_event: FillEvent) -> None:
        """
        Upon receipt of a FillEvent, the PortfolioHandler converts
        the event into a transaction that gets stored in the Portfolio
        object. This ensures that the broker and the local portfolio
        are "in sync".

        In addition, for backtesting purposes, the portfolio value can
        be reasonably estimated in a realistic manner, simply by
        modifying how the ExecutionHandler object handles slippage,
        transaction costs, liquidity and market impact.
        """
        action = fill_event.action
        ticker = fill_event.ticker
        quantity = fill_event.quantity
        price = fill_event.price
        commission = fill_event.commission
        # Create or modify the position from the fill info
        self.portfolio.transact_position(action, ticker, quantity, price, commission)

    def on_order(self, order_event: OrderEvent) -> None:
        """
        :param order_event:
        :return:
        """
        # Place orders onto events queue
        self.events_queue.put(order_event)

    def on_fill(self, fill_event: FillEvent):
        """
        This is called by the backtester or live trading architecture
        to take a FillEvent and update the Portfolio object with new
        or modified Positions.

        In a backtesting environment these FillEvents will be simulated
        by a model representing the execution, whereas in live trading
        they will come directly from a brokerage (such as Interactive
        Brokers).
        """
        self._convert_fill_to_portfolio_update(fill_event)

    def update_portfolio_value(self) -> None:
        """
        Update the portfolio to reflect current market value as
        based on last bid/ask of each ticker.
        """
        self.portfolio.update_portfolio()
