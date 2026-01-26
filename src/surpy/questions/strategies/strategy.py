import polars as pl
from abc import ABC, abstractmethod

from .single_strategy import SingleStrategy
from ..const import QuestionType


class QuestionStrategy(ABC):
    @abstractmethod
    def base_count(self) -> int:
        pass

    @abstractmethod
    def missing(self) -> int:
        pass

    @abstractmethod
    def options_base_count(self) -> pl.DataFrame:
        pass

    @abstractmethod
    def descriptive_statistic(self) -> pl.DataFrame:
        pass


class QuestionStrategyFactory:
    _strategies = {
        QuestionType.Single: SingleStrategy,
        QuestionType.Multiple: "MultipleStrategyHolder",
        QuestionType.Rank: "RankStrategyHolder",
        QuestionType.Open: "OpenStrategyHolder",
    }

    @classmethod
    def get_strategy(cls, type: QuestionType):
        return cls._strategies[type]
