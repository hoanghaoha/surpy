from enum import Enum


class QuestionType(Enum):
    Single = "single_choice"
    Multiple = "multiple_choice"
    Number = "number"
    Rank = "rank"
    Text = "text"
    MatrixSingle = "matrix_single_choice"
    MatrixMultiple = "matrix_multiple_choice"


class Identifier(str, Enum):
    Multiple = "_"
    Matrix = "."
    Rank = "#"
    Id = "ID"
