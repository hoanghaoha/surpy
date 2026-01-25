from enum import Enum


class QuestionType(Enum):
    Single = "Single Choice"
    Multiple = "Multiple Choice"
    Rank = "Rank"
    Open = "Open Answer"


class MatrixType(Enum):
    Single = "Matrix Single Choice"
    Multiple = "Matrix Multiple Choice"


class Seperator(Enum):
    Multiple = "_"
    Matrix = "@"
