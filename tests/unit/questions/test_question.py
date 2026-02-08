import pytest

from surpy.questions.option import Option
from surpy.questions.question import Question
from surpy.config import QuestionType
from surpy.questions.strategies import (
    SingleStrategy,
    MultipleStrategy,
    MatrixSingleStrategy,
    MatrixMultipleStrategy,
    RankStrategy,
    TextStrategy,
    NumberStrategy,
)


@pytest.mark.parametrize(
    "id, qtype, text, data, response_ids, options, sub_items, expected_strategy",
    [
        [
            "Q1",
            QuestionType.Single,
            "test single_choice",
            {1: [1, 2, 3]},
            ["001", "002", "003"],
            ["A", "B", "C"],
            [],
            SingleStrategy,
        ],
        [
            "Q2",
            QuestionType.Multiple,
            "test multiple_choice",
            {1: [0, 0, 1], 2: [1, 0, 1], 3: ["C", 0, 1]},
            ["001", "002", "003"],
            ["A", "B", "C"],
            [],
            MultipleStrategy,
        ],
        [
            "Q3",
            QuestionType.MatrixSingle,
            "test matrix_single_choice",
            {1: [4, 4, 5], 2: [2, 3, 1], 3: [5, 6, 7]},
            ["001", "002", "003"],
            [1, 2, 3, 4, 5],
            ["A", "B", "C"],
            MatrixSingleStrategy,
        ],
        [
            "Q4",
            QuestionType.MatrixMultiple,
            "test multiple_choice",
            {
                1: {1: [0, 0, 1], 2: [1, 1, 1]},
                2: {1: [1, 0, 1], 2: [0, 0, 0]},
                3: {1: [1, 1, 0], 2: [1, 0, 1]},
            },
            ["001", "002", "003"],
            ["X", "Y"],
            ["A", "B", "C"],
            MatrixMultipleStrategy,
        ],
        [
            "Q5",
            QuestionType.Rank,
            "test rank",
            {1: [1, 2, 3], 2: [2, 3, 1], 3: [3, 1, 2]},
            ["001", "002", "003"],
            ["A", "B", "C"],
            [],
            RankStrategy,
        ],
        [
            "Q6",
            QuestionType.Text,
            "test rank",
            {1: ["text 1", "text 2", "text 3"]},
            ["001", "002", "003"],
            [],
            [],
            TextStrategy,
        ],
        [
            "Q7",
            QuestionType.Number,
            "test number",
            {1: [17, 22, 40]},
            ["001", "002", "003"],
            [],
            [],
            NumberStrategy,
        ],
    ],
)
def test_question_create_validation(
    id, qtype, text, data, response_ids, options, sub_items, expected_strategy
):
    question = Question(
        id=id,
        qtype=qtype,
        text=text,
        data=data,
        response_ids=response_ids,
        options=[Option(index=i, text=op) for i, op in enumerate(options, 1)],
        sub_items=sub_items,
    )

    assert isinstance(question.id, str)
    assert isinstance(question.qtype, QuestionType)
    assert isinstance(question.text, str)
    assert isinstance(question.data, dict)
    assert isinstance(question.response_ids, list)
    assert isinstance(question.options, list)
    assert all([isinstance(op, Option) for op in question.options])
    assert isinstance(question.sub_items, list)
    assert isinstance(question._strategy, expected_strategy)
