from dataclasses import dataclass, field

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
    data: dict
    response_ids: list[str]
    options: list[Option] = field(default_factory=list)
    sub_items: list = field(default_factory=list)

    @property
    def _strategy(self):
        if self.qtype in [QuestionType.MatrixSingle, QuestionType.MatrixMultiple]:
            return _strategies[self.qtype](**self.__dict__)
        return _strategies[self.qtype](**self.__dict__)
