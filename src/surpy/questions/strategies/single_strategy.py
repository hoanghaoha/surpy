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

    def options_base_count(self) -> dict[str, int]:
        return {option.id: option.base_count() for option in self.options}

    def descriptive_statistic(self) -> str:
        return f""""
            Base: {self.base_count()}
            Missing: {self.missing()}
            Description:
                {[f"{opt}: {opt_base_count}" for opt, opt_base_count in self.options_base_count().items()]}
        """
