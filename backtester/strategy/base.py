from abc import ABC, abstractmethod
from queue import Queue
from typing import Dict

import pandas as pd

from backtester.event import OrderEvent, BarEvent, TickEvent, EODEvent
from backtester.portfolio_handler import PortfolioHandler


class Strategy(ABC):
    """
    AbstractStrategy is an abstract base class providing an interface for
    all subsequent (inherited) strategy handling objects.

    The goal of a (derived) Strategy object is to generate Signal
    objects for particular symbols based on the inputs of ticks
    generated from a PriceHandler (derived) object.

    This is designed to work both with historic and live data as
    the Strategy object is agnostic to data location.
    """

    @abstractmethod
    def on_bar(self, event):
        pass

    @abstractmethod
    def on_tick(self, event):
        pass

    @abstractmethod
    def on_eod(self, event):
        pass


class PortfolioOptimizationBaseClass(Strategy):

    def __init__(self, portfolio_handler: PortfolioHandler, events_queue: Queue) -> None:
        self.portfolio_handler = portfolio_handler
        self.events_queue = events_queue

    def liquidate_portfolio(self) -> None:
        for name, position in self.portfolio_handler.portfolio.positions.items():
            if position.quantity > 0:
                self.events_queue.put(OrderEvent(ticker=position.ticker, action="SLD", quantity=abs(position.quantity)))
            elif position.quantity < 0:
                self.events_queue.put(OrderEvent(ticker=position.ticker, action="BOT", quantity=abs(position.quantity)))
        return None

    @abstractmethod
    def optimize_portfolio(self, prices: pd.DataFrame) -> Dict[str, int]:
        pass

    @abstractmethod
    def on_bar(self, event: BarEvent) -> None:
        pass

    @abstractmethod
    def on_tick(self, event: TickEvent) -> None:
        pass

    @abstractmethod
    def on_eod(self, event: EODEvent) -> None:
        pass
