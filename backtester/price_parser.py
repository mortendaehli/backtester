from typing import Union


class PriceParser(object):

    """Parse Methods. Multiplies a float out into an int if needed."""
    @staticmethod
    def parse(x: Union[str, float, int]) -> float:
        return float(x)

    @staticmethod
    def display(x: Union[str, float, int]) -> float:
        return round(float(x), 2)
