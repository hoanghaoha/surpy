from dataclasses import dataclass

from .const import QuestionType
from .option import Option
from .response import Response
from .strategies.strategy import QuestionStrategyFactory


@dataclass
class Question:
    id: str
    type: QuestionType
    text: str
    options: list[Option]
    responses: list[Response]

    @property
    def _strategy(self):
        return QuestionStrategyFactory.get_strategy(self.type)
