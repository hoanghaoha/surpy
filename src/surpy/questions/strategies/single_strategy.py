import polars as pl

from .strategy import QuestionStrategy
from ..option import Option
from ..response import Response


class SingleStrategy(QuestionStrategy):
    def __init__(self, options: list[Option], responses: list[Response]):
        self.options = options
        self.responses = responses

    def base_count(self) -> int:
        return sum((1 if response.answer else 0 for response in self.responses))

    def missing(self) -> int:
        return len(self.responses) - self.base_count()

    def options_base_count(self) -> pl.DataFrame:
        pass

    def descriptive_statistic(self) -> pl.DataFrame:
        pass
