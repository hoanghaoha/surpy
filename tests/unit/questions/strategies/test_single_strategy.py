import pytest
import polars as pl
from polars.testing import assert_frame_equal

from surpy.config import Identifier
from surpy.questions.strategies.single_strategy import (
    _to_number_data,
    _to_text_data,
    SingleStrategy,
)
from surpy.questions.option import Option


@pytest.mark.parametrize(
    "data, option_mapping, number_data",
    [
        [["A", "B", "C"], {"A": 1, "B": 2, "C": 3}, [1, 2, 3]],
        [[1, 2, 3], {"A": 1, "B": 2, "C": 3}, [1, 2, 3]],
        [["A", "B", None], {"A": 1, "B": 2, "C": 3}, [1, 2, None]],
        [[1, 2, None], {"A": 1, "B": 2, "C": 3}, [1, 2, None]],
        [["A", "B", ""], {"A": 1, "B": 2, "C": 3}, [1, 2, None]],
    ],
)
def test_to_number_data(data, option_mapping, number_data):
    assert number_data == _to_number_data(data=data, option_mapping=option_mapping)


@pytest.mark.parametrize(
    "data, option_mapping, number_data",
    [
        [[1, 2, 3], {1: "A", 2: "B", 3: "C"}, ["A", "B", "C"]],
        [[1, 2, None], {1: "A", 2: "B", 3: "C"}, ["A", "B", ""]],
    ],
)
def test_to_text_data(data, option_mapping, number_data):
    assert number_data == _to_text_data(data=data, option_mapping=option_mapping)


@pytest.fixture(params=[[1, 2, 3, 2, 1, 2], ["A", "B", "C", "B", "A", "B"]])
def single_strategy_without_none(request):
    return SingleStrategy(
        id="Q1",
        text="Test Single Strategy",
        options=[
            Option(index=1, text="A"),
            Option(index=2, text="B"),
            Option(index=3, text="C"),
        ],
        response_ids=[f"00{i}" for i in range(1, 7)],
        data={1: request.param},
    )


def test_single_strategy_without_none(single_strategy_without_none: SingleStrategy):
    assert single_strategy_without_none._option_mapping(_type="t2n") == {
        "A": 1,
        "B": 2,
        "C": 3,
    }
    assert single_strategy_without_none._option_mapping(_type="n2t") == {
        1: "A",
        2: "B",
        3: "C",
    }
    assert single_strategy_without_none.number_data == [1, 2, 3, 2, 1, 2]
    assert single_strategy_without_none.text_data == ["A", "B", "C", "B", "A", "B"]

    assert_frame_equal(
        single_strategy_without_none.get_df("number"),
        pl.DataFrame(
            {Identifier.Id: [f"00{i}" for i in range(1, 7)], "Q1": [1, 2, 3, 2, 1, 2]}
        ),
    )

    assert_frame_equal(
        single_strategy_without_none.get_df("text"),
        pl.DataFrame(
            {
                Identifier.Id: [f"00{i}" for i in range(1, 7)],
                "Q1": ["A", "B", "C", "B", "A", "B"],
            }
        ),
    )

    assert_frame_equal(
        single_strategy_without_none.describe(),
        pl.DataFrame(
            {
                "Q1": ["A", "B", "C"],
                "count": [2, 3, 1],
                "percent": [2 / 6, 3 / 6, 1 / 6],
                "cum_percent": [2 / 6, 5 / 6, 6 / 6],
            },
            schema={
                "Q1": pl.String,
                "count": pl.UInt32,
                "percent": pl.Float64,
                "cum_percent": pl.Float64,
            },
        ),
    )


@pytest.fixture(
    params=[
        [1, 2, None, 2, 1, 2],
        ["A", "B", "", "B", "A", "B"],
        ["A", "B", None, "B", "A", "B"],
    ]
)
def single_strategy_with_none(request):
    return SingleStrategy(
        id="Q1",
        text="Test Single Strategy",
        options=[
            Option(index=1, text="A"),
            Option(index=2, text="B"),
            Option(index=3, text="C"),
        ],
        response_ids=[f"00{i}" for i in range(1, 7)],
        data={1: request.param},
    )


def test_single_strategy_with_none(single_strategy_with_none: SingleStrategy):
    assert single_strategy_with_none.number_data == [1, 2, None, 2, 1, 2]
    assert single_strategy_with_none.text_data == ["A", "B", "", "B", "A", "B"]

    assert_frame_equal(
        single_strategy_with_none.get_df("number"),
        pl.DataFrame(
            {
                Identifier.Id: [f"00{i}" for i in range(1, 7)],
                "Q1": [1, 2, None, 2, 1, 2],
            }
        ),
    )

    assert_frame_equal(
        single_strategy_with_none.get_df("text"),
        pl.DataFrame(
            {
                Identifier.Id: [f"00{i}" for i in range(1, 7)],
                "Q1": ["A", "B", "", "B", "A", "B"],
            }
        ),
    )

    assert_frame_equal(
        single_strategy_with_none.describe(),
        pl.DataFrame(
            {
                "Q1": ["", "A", "B"],
                "count": [1, 2, 3],
                "percent": [1 / 6, 2 / 6, 3 / 6],
                "cum_percent": [1 / 6, 3 / 6, 6 / 6],
            },
            schema={
                "Q1": pl.String,
                "count": pl.UInt32,
                "percent": pl.Float64,
                "cum_percent": pl.Float64,
            },
        ),
    )
