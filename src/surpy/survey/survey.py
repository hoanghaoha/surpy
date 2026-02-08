from ..questions.question import Question


class Survey:
    def __init__(self, name: str, questions: list[Question]):
        self.name = name
        self.questions = questions
