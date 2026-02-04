import polars as pl
from abc import ABC, abstractmethod


class QuestionStrategy(ABC):
    @abstractmethod
    def _validate_data(self, data: dict) -> None:
        pass

    @property
    @abstractmethod
    def dtype(self) -> str:
        pass

    @abstractmethod
    def get_df(self) -> pl.DataFrame:
        pass

    @abstractmethod
    def describe(self) -> pl.DataFrame:
        pass
