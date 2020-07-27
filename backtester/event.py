from typing import Optional
from datetime import datetime, date
from enum import Enum


class EventType(Enum):
    NAN = 0
    BAR = 1
    TICK = 2
    ORDER = 3
    FILL = 4
    EOD = 5


class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    type = EventType.NAN

    @property
    def typename(self):
        return self.type.name


class EODEvent(Event):

    def __init__(self, time: datetime) -> None:
        """
        End-of-day-event

        :param time: The timestamp of the EOD-event
        """
        self.type = EventType.EOD
        self.time = time

    def __str__(self):
        return f"Type: {self.type}, Time: {self.time}"

    def __repr__(self):
        return str(self)


class TickEvent(Event):

    def __init__(self, ticker: str, time: datetime, bid: float, ask: float) -> None:
        """
        Tick-event

        :param ticker: The ticker symbol, e.g. 'GOOG'.
        :param time: The timestamp of the tick
        :param bid: The best bid price at the time of the tick.
        :param ask: The best ask price at the time of the tick.
        """
        self.type = EventType.TICK
        self.ticker = ticker
        self.time = time
        self.bid = bid
        self.ask = ask

    def __str__(self):
        return f"Type: {self.type}, Ticker: {self.ticker}, Time: {self.time}, Bid: {self.bid}, Ask: {self.ask}"

    def __repr__(self):
        return str(self)


class BarEvent(Event):
    def __init__(
            self, ticker: str, time: datetime, period: int,
            open_price: float, high_price: float, low_price: float,
            close_price: float, volume: float
    ):
        """
        OHLCV Bar-event:

        :param ticker: The ticker symbol, e.g. 'GOOG'.
        :param time: The timestamp of the bar
        :param period: The time period covered by the bar in seconds
        :param open_price: The unadjusted opening price of the bar
        :param high_price: The unadjusted high price of the bar
        :param low_price: The unadjusted low price of the bar
        :param close_price: The unadjusted close price of the bar
        :param volume: The volume of trading within the bar
        """
        self.type = EventType.BAR
        self.ticker = ticker
        self.time = time
        self.period = period
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.volume = volume
        self.period_readable = self._readable_period()

    def _readable_period(self):
        """
        Creates a human-readable period from the number
        of seconds specified for 'period'.

        For instance, converts:
        * 1 -> '1sec'
        * 5 -> '5secs'
        * 60 -> '1min'
        * 300 -> '5min'

        If no period is found in the lookup table, the human
        readable period is simply passed through from period,
        in seconds.
        """
        lut = {
            1: "1sec",
            5: "5sec",
            10: "10sec",
            15: "15sec",
            30: "30sec",
            60: "1min",
            300: "5min",
            600: "10min",
            900: "15min",
            1800: "30min",
            3600: "1hr",
            86400: "1day",
            604800: "1wk"
        }
        if self.period in lut:
            return lut[self.period]
        else:
            return "%ssec" % str(self.period)

    def __str__(self):
        return f"Type: {self.type}, Ticker: {self.ticker}], Time: {self.time}, Period: {self.period_readable}, " \
               f"Open: {self.open_price}, High: {self.high_price}, Low: {self.low_price}, Close: {self.close_price}, " \
               f"Volume: {self.volume}"

    def __repr__(self):
        return str(self)


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a ticker (e.g. GOOG), action (BOT or SLD)
    and quantity.
    """
    def __init__(self, ticker: str, action: str, quantity: float):
        """
        Order-event

        :param ticker: The ticker symbol, e.g. 'GOOG'.
        :param action: 'BOT' (for long) or 'SLD' (for short).
        :param quantity: The quantity of shares to transact.
        """
        self.type = EventType.ORDER
        self.ticker = ticker
        self.action = action
        self.quantity = quantity

    def print_order(self):
        """
        Outputs the values within the OrderEvent.
        """
        print(f"Order: Ticker={self.ticker}, Action={self.action}, Quantity={self.quantity}")


class FillEvent(Event):
    """
    Encapsulates the notion of a filled order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.

    Currently does not support filling positions at
    different prices.
    """

    def __init__(
            self, timestamp: datetime, ticker: str,
            action: str, quantity: float,
            exchange: str, price: float,
            commission: float
    ):
        """
        Initialises the FillEvent object.

        :param timestamp: The timestamp when the order was filled.
        :param ticker: The ticker symbol, e.g. 'GOOG'.
        :param action: 'BOT' (for long) or 'SLD' (for short).
        :param quantity: The filled quantity.
        :param exchange: The exchange where the order was filled.
        :param price: The price at which the trade was filled
        :param commission: The brokerage commission for carrying out the trade.
        """
        self.type = EventType.FILL
        self.timestamp = timestamp
        self.ticker = ticker
        self.action = action
        self.quantity = quantity
        self.exchange = exchange
        self.price = price
        self.commission = commission

