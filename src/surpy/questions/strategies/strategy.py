from typing import Literal
import polars as pl
from abc import ABC, abstractmethod


class QuestionStrategy(ABC):
    @abstractmethod
    def get_df(self, dtype: Literal["number", "text"]) -> pl.DataFrame:
        pass

    @abstractmethod
    def describe(self) -> pl.DataFrame:
        pass
