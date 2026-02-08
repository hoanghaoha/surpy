from enum import StrEnum


class QuestionType(StrEnum):
    Single = "single_choice"
    Multiple = "multiple_choice"
    Number = "number"
    Rank = "rank"
    Text = "text"
    MatrixSingle = "matrix_single_choice"
    MatrixMultiple = "matrix_multiple_choice"


class Identifier(StrEnum):
    Multiple = "_"
    Matrix = "."
    Rank = "#"
    Id = "ID"
