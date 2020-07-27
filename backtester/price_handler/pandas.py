from typing import Optional, List, Iterator
from queue import Queue
from datetime import datetime, date
from abc import abstractmethod

import pandas as pd

from backtester.price_handler.base import PriceHandler
from backtester.event import BarEvent, EODEvent, EventType


class OHLCVDataFrameReader:
    def __init__(self):
        pass

    @abstractmethod
    def read_ohlcv(self, ticker_id: int, start: date, end: date) -> pd.DataFrame:
        pass


class OHLCVPriceHandler(PriceHandler):
    def __init__(
            self,
            ticker_ids: List[int],
            ticker_names: List[str],
            events_queue: Queue,
            reader: OHLCVDataFrameReader,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
    ) -> None:
        """

        :param ticker_ids:
        :param ticker_names:
        :param events_queue:
        :param start_date:
        :param end_date:
        """
        self.cnt_backtest = True
        self.events_queue = events_queue
        self.ticker_ids = ticker_ids
        self.ticker_names = ticker_names
        self.tickers = {}
        self.data = {}
        self.reader = reader
        self.start_date = start_date
        self.end_date = end_date
        for ticker_id, ticker_name in zip(self.ticker_ids, self.ticker_names):
            self.subscribe_tickers(ticker_id=ticker_id, ticker_name=ticker_name)

        self.bar_stream = self._merge_sort_ticker_data()

    def istick(self) -> bool:
        return False

    def isbar(self) -> bool:
        return True

    @property
    def continue_backtest(self) -> bool:
        return self.cnt_backtest

    def subscribe_tickers(self, ticker_id: int, ticker_name: str) -> None:
        """
        Will remove any existing tickers...
        """

        if ticker_name not in self.tickers:
            try:
                df = self.reader.read_ohlcv(ticker_id=ticker_id, start=self.start_date, end=self.end_date)
                df = df.reindex(pd.date_range(start=self.start_date, end=min(self.end_date, df.index.max())))
                df.loc[:, :] = df.interpolate()
                df.loc[:, :] = df.bfill().ffill()
                df.columns = ["close_price"]
                df.loc[:, "ticker_name"] = ticker_name
                df.loc[:, "ticker_id"] = ticker_id

                self.data[ticker_name] = df
                self.tickers[ticker_name] = dict()
            except OSError:
                print(f"Could not subscribe ticker {ticker_name} as no data CSV found for pricing.")
        else:
            print(f"Could not subscribe ticker {ticker_name} as is already subscribed.")

    def _merge_sort_ticker_data(self) -> Iterator:
        df = pd.concat(self.data.values())
        events = df.reset_index().apply(lambda x:
                               BarEvent(
                                   ticker=x["ticker_name"],
                                   time=x["index"],
                                   period=86400,
                                   open_price=x["close_price"],
                                   high_price=x["close_price"],
                                   low_price=x["close_price"],
                                   close_price=x["close_price"],
                                   volume=100000000000000
                               ),
                               axis=1).to_list()
        events = events + df.index.unique().map(lambda x: EODEvent(time=datetime(x.year, x.month, x.day, 23, 59, 59))).to_list()

        events = sorted(events, key=lambda x: x.time, reverse=False)
        return iter(events)

    def _store_event(self, event):
        """
        Store price event for closing price and adjusted closing price
        """
        self.tickers[event.ticker]["close"] = event.close_price
        self.tickers[event.ticker]["timestamp"] = event.time

    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        try:
            event = next(self.bar_stream)
        except StopIteration:
            self.cnt_backtest = False
            return

        # Store event
        if event.type == EventType.BAR:
            self._store_event(event)

        # Send event to queue
        self.events_queue.put(event)
