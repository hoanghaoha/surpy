from enum import Enum


class QuestionType(Enum):
    Single = "single_choice"
    Multiple = "multiple_choice"
    Rank = "rank"
    Text = "text"
    MatrixSingle = "matrix_single_choice"
    MatrixMultiple = "matrix_multiple_choice"


class Seperator(Enum):
    Multiple = "_"
    Matrix = "."
