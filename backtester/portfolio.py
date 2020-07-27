from backtester.position import Position
from backtester.price_handler.base import PriceHandler


class Portfolio(object):
    def __init__(self, price_handler: PriceHandler, cash: float) -> None:
        """
        On creation, the Portfolio object contains no
        positions and all values are "reset" to the initial
        cash, with no PnL - realised or unrealised.

        Note that realised_pnl is the running tally pnl from closed
        positions (closed_pnl), as well as realised_pnl
        from currently open positions.
        """
        self.price_handler = price_handler
        self.init_cash = cash
        self.equity = cash
        self.cur_cash = cash
        self.positions = {}
        self.closed_positions = []
        self.realised_pnl = 0
        self.unrealised_pnl = 0

    def update_portfolio(self) -> None:
        """
        Updates the value of all positions that are currently open.
        Value of closed positions is tallied as self.realised_pnl.
        """
        self.unrealised_pnl = 0
        self.equity = self.realised_pnl
        self.equity += self.init_cash

        for ticker in self.positions:
            pt = self.positions[ticker]
            if self.price_handler.istick():
                bid, ask = self.price_handler.get_best_bid_ask(ticker=ticker)
            else:
                close_price = self.price_handler.get_last_close(ticker=ticker)
                bid = close_price
                ask = close_price
            pt.update_market_value(bid=bid, ask=ask)
            self.unrealised_pnl += pt.unrealised_pnl
            self.equity += pt.market_value - pt.cost_basis + pt.realised_pnl

    def print_portfolio(self) -> None:
        print(self.equity)
        for ticker in self.positions:
            pt = self.positions[ticker]
            print(ticker, pt.market_value, pt.quantity)
        print()
        return None

    def _add_position(self, action: str, ticker: str, quantity: float, price: float, commission: float) -> None:
        """
        Adds a new Position object to the Portfolio. This
        requires getting the best bid/ask price from the
        price handler in order to calculate a reasonable
        "market value".

        Once the Position is added, the Portfolio values
        are updated.

        :param action:
        :param ticker:
        :param quantity:
        :param price:
        :param commission:
        :return:
        """
        if ticker not in self.positions:
            if self.price_handler.istick():
                bid, ask = self.price_handler.get_best_bid_ask(ticker=ticker)
            else:
                close_price = self.price_handler.get_last_close(ticker=ticker)
                bid = close_price
                ask = close_price
            position = Position(action=action, ticker=ticker, init_quantity=quantity, init_price=price, init_commission=commission, bid=bid, ask=ask)
            self.positions[ticker] = position
            self.update_portfolio()
        else:
            print(f"Ticker {ticker} is already in the positions list. Could not add a new position.")

    def _modify_position(self, action: str, ticker: str, quantity: float, price: float, commission: float) -> None:
        """
        Modifies a current Position object to the Portfolio.
        This requires getting the best bid/ask price from the
        price handler in order to calculate a reasonable
        "market value".

        Once the Position is modified, the Portfolio values
        are updated.

        :param action:
        :param ticker:
        :param quantity:
        :param price:
        :param commission:
        :return:
        """

        if ticker in self.positions:
            self.positions[ticker].transact_shares(action=action, quantity=quantity, price=price, commission=commission)
            if self.price_handler.istick():
                bid, ask = self.price_handler.get_best_bid_ask(ticker=ticker)
            else:
                close_price = self.price_handler.get_last_close(ticker=ticker)
                bid = close_price
                ask = close_price
            self.positions[ticker].update_market_value(bid=bid, ask=ask)

            if self.positions[ticker].quantity == 0:
                closed = self.positions.pop(ticker)
                self.realised_pnl += closed.realised_pnl
                self.closed_positions.append(closed)

            self.update_portfolio()
        else:
            print(f"Ticker {ticker} not in the current position list. Could not modify a current position.")

    def transact_position(self, action: str, ticker: str, quantity: float, price: float, commission: float) -> None:
        """
        Handles any new position or modification to
        a current position, by calling the respective
        _add_position and _modify_position methods.

        Hence, this single method will be called by the
        PortfolioHandler to update the Portfolio itself.
        """

        if action == "BOT":
            self.cur_cash -= (quantity * price) + commission
        elif action == "SLD":
            self.cur_cash += (quantity * price) - commission

        if ticker not in self.positions:
            self._add_position(action=action, ticker=ticker, quantity=quantity, price=price, commission=commission)
        else:
            self._modify_position(action=action, ticker=ticker, quantity=quantity, price=price, commission=commission)
