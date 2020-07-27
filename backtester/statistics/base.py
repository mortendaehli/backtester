from typing import Optional
import pickle

from abc import ABC, abstractmethod
from datetime import datetime


class Statistics(ABC):
    """
    Statistics is an abstract class providing an interface for
    all inherited statistic classes (live, historic, custom, etc).

    The goal of a Statistics object is to keep a record of useful
    information about one or many trading strategies as the strategy
    is running. This is done by hooking into the main event loop and
    essentially updating the object according to portfolio performance
    over time.

    Ideally, Statistics should be subclassed according to the strategies
    and timeframes-traded by the user. Different trading strategies
    may require different metrics or frequencies-of-metrics to be updated,
    however the example given is suitable for longer timeframes.
    """


    @abstractmethod
    def update(self, timestamp: datetime):
        pass

    @abstractmethod
    def get_results(self):
        pass

    @abstractmethod
    def plot_results(self, filename: Optional[str]):
        pass

    @abstractmethod
    def save(self, filename):
        pass

    @classmethod
    def load(cls, filename):
        with open(filename, 'rb') as fd:
            stats = pickle.load(fd)
        return stats

