import queue
from queue import Queue

from typing import Optional
from datetime import datetime

from backtester.event import EventType
from backtester.price_handler.base import PriceHandler
from backtester.portfolio_handler import PortfolioHandler
from backtester.execution_handler.base import ExecutionHandler
from backtester.statistics.base import Statistics
from backtester.strategy.base import Strategy


class TradingSession(object):
    """
    Enscapsulates the settings and components for
    carrying out either a backtest or live trading session.
    """
    def __init__(
            self,
            strategy: Strategy,
            price_handler: PriceHandler,
            execution_handler: ExecutionHandler,
            portfolio_handler: PortfolioHandler,
            events_queue: Queue,
            statistics: Optional[Statistics] = None,
            live: Optional[bool] = False,
            end_session_time: Optional[datetime] = None,
    ) -> None:
        """
        Set up the backtest variables according to
        what has been passed in. The Strategy, PriceHandler,
        ExecutionHandler and PortfolioHandler can be any implementation
        of the bases classes.

        :param strategy: A Strategy object that acts on events.
        :param price_handler: A price handler
        :param execution_handler: An execution handler
        :param portfolio_handler: A portfolio handler
        :param events_queue: Queue of events.
        :param statistics: Optional Statistics instance.
        :param live: Optional. None or True for backtesting, or False for live.
        :param end_session_time: Time of end session for live trading.
        """
        self.strategy = strategy
        self.events_queue = events_queue
        self.price_handler = price_handler
        self.portfolio_handler = portfolio_handler
        self.execution_handler = execution_handler
        self.statistics = statistics
        self.live = live
        self.cur_time = datetime(1900, 1, 1)
        self.end_session_time = end_session_time

        if self.live:
            if self.end_session_time is None:
                raise Exception("Must specify an end_session_time when live trading")

    def _continue_loop_condition(self) -> bool:
        if not self.live:
            return self.price_handler.continue_backtest
        else:
            return datetime.now() < self.end_session_time

    def _run_session(self) -> None:
        """
        Carries out an infinite while loop that polls the
        events queue and directs each event to the respective handlers.
        emptied.
        """
        if not self.live:
            print("Running Backtest...")
        else:
            print(f"Running Realtime Session until {self.end_session_time}")

        while self._continue_loop_condition():
            try:
                event = self.events_queue.get(False)
            except queue.Empty:
                self.price_handler.stream_next()
            else:
                if event is not None:
                    if event.type == EventType.EOD:
                        self.cur_time = event.time
                        self.strategy.on_eod(event=event)
                        self.portfolio_handler.update_portfolio_value()
                        self.statistics.update(event.time)
                    elif event.type == EventType.BAR:
                        self.cur_time = event.time
                        self.strategy.on_bar(event)
                    elif event.type == EventType.TICK:
                        self.cur_time = event.time
                        self.strategy.on_tick(event)
                    elif event.type == EventType.ORDER:
                        self.execution_handler.execute_order(event)
                    elif event.type == EventType.FILL:
                        self.portfolio_handler.on_fill(event)
                    else:
                        raise NotImplemented(f"Unsupported event.type {event.type}")

    def start_trading(self, testing: bool = False, filename: Optional[str] = None) -> Optional[dict]:
        """
        Runs either a backtest or live session, and outputs performance when complete.
        """
        self._run_session()
        if self.statistics:
            results = self.statistics.get_results()
            print("---------------------------------")
            print("Backtest complete.")
            print(f"Sharpe Ratio: {results['sharpe']:0.2f}")
            print(f"Max Drawdown: {results['max_drawdown_pct'] * 100:0.2f}")
            if not testing:
                self.statistics.plot_results(filename=filename)
            return results
