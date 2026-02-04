from ..questions.question import Question


class Survey:
    def __init__(self, questions: list[Question]):
        self.questions = questions
