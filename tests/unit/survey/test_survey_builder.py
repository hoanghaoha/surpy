import pytest

from surpy.survey.survey_builder import (
    _load_data_single,
    _load_data_multiple,
    _load_data_matrix_single,
    _load_data_matrix_multiple,
    _load_data_rank,
    _load_survey_data,
)
from surpy.config import Identifier


@pytest.mark.parametrize(
    "survey_data, question_code, question_data",
    [
        [{}, "Q1", [1, 2, 3]],
        [{}, "Q1", ["A", "B", "C"]],
        [{"Q0": {1: [1, 2, 3]}}, "Q1", [1, 2, 3]],
    ],
)
def test_load_data_single(survey_data, question_code, question_data):
    _load_data_single(survey_data, question_code, question_data)

    assert isinstance(survey_data, dict)
    assert all([isinstance(key, str) for key in survey_data.keys()])
    assert all([isinstance(value, dict) for value in survey_data.values()])
    assert all([len(value) == 1 for value in survey_data.values()])
    assert all([1 in value for value in survey_data.values()])
    assert all([len(value[1]) == len(question_data) for value in survey_data.values()])


@pytest.mark.parametrize(
    "survey_data, question_code, question_data",
    [
        [{}, f"Q1{Identifier.Multiple}1", [0, 1, 0]],
        [{}, f"Q1{Identifier.Multiple}2", ["A", "", "C"]],
        [{"Q1": {1: [0, 1, 0]}}, f"Q1{Identifier.Multiple}2", ["A", "B", ""]],
    ],
)
def test_load_data_multiple(survey_data, question_code, question_data):
    _load_data_multiple(survey_data, question_code, question_data)

    assert isinstance(survey_data, dict)
    assert all([isinstance(key, str) for key in survey_data.keys()])
    assert all([isinstance(value, dict) for value in survey_data.values()])
    assert all(
        [isinstance(k, int) for value in survey_data.values() for k in value.keys()]
    )
    assert all(
        [isinstance(v, list) for value in survey_data.values() for v in value.values()]
    )
    assert all(
        [
            len(v) == len(question_data)
            for value in survey_data.values()
            for v in value.values()
        ]
    )


@pytest.mark.parametrize(
    "survey_data, question_code, question_data",
    [
        [{}, f"Q1{Identifier.Matrix}2", [1, 2, 3]],
        [{}, f"Q1{Identifier.Matrix}2", ["A", "B", "C"]],
        [{"Q1": {1: [1, 1, 2]}}, f"Q1{Identifier.Matrix}2", [1, 2, 3]],
    ],
)
def test_load_data_matrix_single(survey_data, question_code, question_data):
    _load_data_matrix_single(survey_data, question_code, question_data)

    assert isinstance(survey_data, dict)
    assert all([isinstance(key, str) for key in survey_data.keys()])
    assert all([isinstance(value, dict) for value in survey_data.values()])
    assert all(
        [isinstance(k, int) for value in survey_data.values() for k in value.keys()]
    )
    assert all(
        [isinstance(v, list) for value in survey_data.values() for v in value.values()]
    )
    assert all(
        [
            len(v) == len(question_data)
            for value in survey_data.values()
            for v in value.values()
        ]
    )


@pytest.mark.parametrize(
    "survey_data, question_code, question_data",
    [
        [{}, f"Q1{Identifier.Matrix}1{Identifier.Multiple}2", [1, 2, 3]],
        [{}, f"Q1{Identifier.Matrix}1{Identifier.Multiple}2", ["A", "B", "C"]],
        [
            {"Q1": {1: {1: [1, 2, 3]}}},
            f"Q1{Identifier.Matrix}1{Identifier.Multiple}2",
            [1, 2, 3],
        ],
    ],
)
def test_load_data_matrix_multiple(survey_data, question_code, question_data):
    _load_data_matrix_multiple(survey_data, question_code, question_data)

    assert isinstance(survey_data, dict)
    assert all([isinstance(key, str) for key in survey_data.keys()])
    assert all([isinstance(value, dict) for value in survey_data.values()])
    assert all(
        [isinstance(k, int) for value in survey_data.values() for k in value.keys()]
    )
    assert all(
        [
            isinstance(sub_value, dict)
            for value in survey_data.values()
            for sub_value in value.values()
        ]
    )
    assert all(
        [
            all([isinstance(k, int), isinstance(v, list)])
            for value in survey_data.values()
            for sub_value in value.values()
            for k, v in sub_value.items()
        ]
    )
    assert all(
        [
            len(v) == len(question_data)
            for value in survey_data.values()
            for sub_value in value.values()
            for v in sub_value.values()
        ]
    )


@pytest.mark.parametrize(
    "survey_data, question_code, question_data",
    [
        [{}, f"Q1{Identifier.Rank}2", [1, 2, 3]],
        [{}, f"Q1{Identifier.Rank}2", ["A", "B", "C"]],
        [{"Q1": {1: [1, 1, 2]}}, f"Q1{Identifier.Rank}2", [1, 2, 3]],
    ],
)
def test_load_data_rank(survey_data, question_code, question_data):
    _load_data_rank(survey_data, question_code, question_data)

    assert isinstance(survey_data, dict)
    assert all([isinstance(key, str) for key in survey_data.keys()])
    assert all([isinstance(value, dict) for value in survey_data.values()])
    assert all(
        [isinstance(k, int) for value in survey_data.values() for k in value.keys()]
    )
    assert all(
        [isinstance(v, list) for value in survey_data.values() for v in value.values()]
    )
    assert all(
        [
            len(v) == len(question_data)
            for value in survey_data.values()
            for v in value.values()
        ]
    )


@pytest.fixture
def raw_data():
    return {
        "ID": ["001", "002", "003"],
        "Q1": [1, 2, 3],
        f"Q2{Identifier.Multiple}1": [0, 1, 0],
        f"Q2{Identifier.Multiple}2": [1, 1, 0],
        f"Q2{Identifier.Multiple}3": [1, 1, 1],
        f"Q3{Identifier.Matrix}1": [4, 2, 5],
        f"Q3{Identifier.Matrix}2": [2, 5, 5],
        f"Q3{Identifier.Matrix}3": [1, 4, 3],
        f"Q4{Identifier.Matrix}1{Identifier.Multiple}1": [0, 1, 0],
        f"Q4{Identifier.Matrix}1{Identifier.Multiple}2": [1, 1, 0],
        f"Q4{Identifier.Matrix}2{Identifier.Multiple}1": [1, 1, 1],
        f"Q4{Identifier.Matrix}2{Identifier.Multiple}2": [1, 0, 0],
        f"Q5{Identifier.Rank}1": [1, 2, 3],
        f"Q5{Identifier.Rank}2": [2, 3, 1],
        f"Q5{Identifier.Rank}3": [3, 1, 2],
        "Q6": [20, 10, 100],
    }


def test_load_survey_data(raw_data):
    survey_data = _load_survey_data(raw_data)

    assert survey_data == {
        "ID": {1: ["001", "002", "003"]},
        "Q1": {1: [1, 2, 3]},
        "Q2": {1: [0, 1, 0], 2: [1, 1, 0], 3: [1, 1, 1]},
        "Q3": {1: [4, 2, 5], 2: [2, 5, 5], 3: [1, 4, 3]},
        "Q4": {1: {1: [0, 1, 0], 2: [1, 1, 0]}, 2: {1: [1, 1, 1], 2: [1, 0, 0]}},
        "Q5": {1: [1, 2, 3], 2: [2, 3, 1], 3: [3, 1, 2]},
        "Q6": {1: [20, 10, 100]},
    }
