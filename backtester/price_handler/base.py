from typing import Union, Optional, Tuple, Any
from abc import ABC, abstractmethod

from backtester.event import BarEvent, TickEvent


class PriceHandler(ABC):
    """
    PriceHandler is a base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) PriceHandler object is to output a set of
    TickEvents or BarEvents for each financial instrument and place
    them into an event queue.

    This will replicate how a live strategy would function as current
    tick/bar data would be streamed via a brokerage. Thus a historic and live
    system will be treated identically by the rest of the QSTrader suite.
    """
    tickers: dict = None
    data: dict = None

    @abstractmethod
    def istick(self) -> bool:
        pass

    @abstractmethod
    def isbar(self) -> bool:
        pass

    @abstractmethod
    def stream_next(self) -> None:
        pass

    @property
    def continue_backtest(self):
        raise NotImplementedError("This method has not been implemented.")

    def unsubscribe_ticker(self, ticker):
        """
        Unsubscribes the price handler from a current ticker symbol.
        """
        try:
            self.tickers.pop(ticker, None)
            self.data.pop(ticker, None)
        except KeyError:
            print("Could not unsubscribe ticker %s as it was never subscribed." % ticker)

    def get_last_timestamp(self, ticker):
        """
        Returns the most recent actual timestamp for a given ticker
        """
        if ticker in self.tickers:
            timestamp = self.tickers[ticker]["timestamp"]
            return timestamp
        else:
            print("Timestamp for ticker %s is not available from the %s." % (ticker, self.__class__.__name__))
            return None

    def _store_event(self, event: Union[BarEvent, TickEvent]) -> None:
        """
        Store price event for closing price and adjusted closing price
        """
        if event.type == BarEvent:
            ticker = event.ticker
            self.tickers[ticker]["close"] = event.close_price
            self.tickers[ticker]["adj_close"] = event.close_price
            self.tickers[ticker]["timestamp"] = event.time
        elif event.type == TickEvent:
            ticker = event.ticker
            self.tickers[ticker]["bid"] = event.bid
            self.tickers[ticker]["ask"] = event.ask
            self.tickers[ticker]["timestamp"] = event.time
        else:
            raise NotImplementedError(f"Event-type {event.type} has not been implemented for the price-handler.")

    def get_best_bid_ask(self, ticker: str) -> Tuple[Any, Any]:
        """
        Returns the most recent bid/ask price for a ticker.
        """
        if ticker in self.tickers:
            if "bid" in self.tickers[ticker] & "ask" in self.tickers[ticker]:
                bid = self.tickers[ticker]["bid"]
                ask = self.tickers[ticker]["ask"]
                return bid, ask
        print(f"Bid/ask values for ticker {ticker} are not available from the PriceHandler.")
        return None, None

    def get_last_close(self, ticker: str) -> Optional[float]:
        """
        Returns the most recent actual (unadjusted) closing price.
        """
        if ticker in self.tickers:
            if "close" in self.tickers[ticker]:
                close_price = self.tickers[ticker]["close"]
                return close_price
        print(f"Close price for ticker {ticker} is not available from the PriceHandler.")
        return None
