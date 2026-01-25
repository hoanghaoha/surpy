from dataclasses import dataclass

from .const import Seperator


@dataclass
class Option:
    question_id: str
    index: int
    text: str
    respondents: list[str]

    @property
    def id(self):
        return f"{self.question_id}{Seperator.Multiple}{self.index}"

    def base_count(self):
        return len(self.respondents)
