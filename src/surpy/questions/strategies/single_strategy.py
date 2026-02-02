import polars as pl

from .strategy import QuestionStrategy
from ..option import Option


class SingleStrategy(QuestionStrategy):
    def __init__(self, options: list[Option], data: list):
        self.options = options
        self.data = data

    def get_df(self) -> pl.DataFrame:
        return pl.DataFrame()

    def describe(self) -> pl.DataFrame:
        return pl.DataFrame()
