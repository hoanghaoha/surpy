from dataclasses import dataclass


@dataclass
class Response:
    id: str
    answer: int | list[int]
    question_id: str
