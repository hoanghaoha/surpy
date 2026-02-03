from dataclasses import dataclass

from ..config import QuestionType
from .option import Option
from .strategies.strategy import QuestionStrategyFactory


@dataclass
class Question:
    id: str
    qtype: QuestionType
    text: str
    options: list[Option]
    data: list
    response_ids: list[str]

    @property
    def _strategy(self):
        return QuestionStrategyFactory.get_strategy(self.qtype)
