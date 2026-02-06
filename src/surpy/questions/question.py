from dataclasses import dataclass

from .option import Option
from . import strategies
from ..config import QuestionType


_strategies = {
    QuestionType.Single: strategies.SingleStrategy,
    QuestionType.Multiple: strategies.MultipleStrategy,
    QuestionType.MatrixSingle: strategies.MatrixSingleStrategy,
    QuestionType.MatrixMultiple: strategies.MatrixMultipleStrategy,
    QuestionType.Number: strategies.NumberStrategy,
    QuestionType.Rank: strategies.RankStrategy,
    QuestionType.Text: strategies.TextStrategy,
}


@dataclass
class Question:
    id: str
    qtype: QuestionType
    text: str
    options: list[Option]
    data: dict
    response_ids: list[str]

    @property
    def _strategy(self):
        return _strategies[self.qtype](**self.__dict__)
