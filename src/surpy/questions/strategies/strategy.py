import polars as pl
from abc import ABC, abstractmethod

from .single_strategy import SingleStrategy
from ...config import QuestionType


class QuestionStrategy(ABC):
    @abstractmethod
    def get_df(self) -> pl.DataFrame:
        pass

    @abstractmethod
    def describe(self) -> pl.DataFrame:
        pass


class QuestionStrategyFactory:
    _strategies = {
        QuestionType.Single: SingleStrategy,
        QuestionType.Multiple: "MultipleStrategyHolder",
        QuestionType.Rank: "RankStrategyHolder",
        QuestionType.Text: "OpenStrategyHolder",
    }

    @classmethod
    def get_strategy(cls, type: QuestionType):
        return cls._strategies[type]
