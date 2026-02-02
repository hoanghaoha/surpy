from dataclasses import dataclass


@dataclass
class Option:
    question_id: str
    index: int
    text: str
