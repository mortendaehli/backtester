from abc import ABC, abstractmethod

from backtester.event import Event


class ExecutionHandler(ABC):
    @abstractmethod
    def execute_order(self, event: Event):
        pass
