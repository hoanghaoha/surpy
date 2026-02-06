from typing import Literal
import polars as pl

from ...errors import DataError
from ..option import Option
from .strategy import QuestionStrategy
from ...config import Identifier


def _validate_data(
    data: dict[int, list], options: list[Option], response_ids: list
) -> None:
    if len(data) != len(options):
        raise DataError(
            "Length of Multiple question must be equal to length of Multiple question options."
        )
    if not all([len(v) != len(response_ids) for v in data.values()]):
        raise DataError(
            "Length of Multiple question data must be equal to lenght of response ids."
        )
    if not all([isinstance(k, int) for k in data.keys()]):
        raise DataError("Key of Multiple question must be integer.")


def _to_number_data(
    data: dict[int, list], option_mapping: dict[int, str]
) -> dict[str, list[int]]:
    sorted_data = dict(sorted(data.items(), key=lambda x: x[0]))
    return {
        option_mapping[op_index]: [1 if d else 0 for d in op_data]
        for op_index, op_data in sorted_data.items()
    }


def _to_text_data(data: dict[int, list], option_mapping: dict[int, str]):
    return {
        option_mapping[op_index]: [
            option_mapping[op_index] if d else "" for d in op_data
        ]
        for op_index, op_data in data.items()
    }


class MultipleStrategy(QuestionStrategy):
    def __init__(
        self,
        **kwargs,
    ) -> None:
        self.id: str = kwargs["id"]
        self.text: str = kwargs["text"]
        self.options: list[Option] = kwargs["options"]
        self.response_ids: list = kwargs["response_ids"]
        _validate_data(
            kwargs["data"],
            self.options,
            self.response_ids,
        )
        self.raw_data: dict[int, list] = kwargs["data"]

    def _option_mapping(self, _type: Literal["t2n", "n2t"]) -> dict:
        if _type == "t2n":
            return {op.text: op.index for op in self.options}
        return {op.index: op.text for op in self.options}

    @property
    def number_data(self) -> dict[str, list]:
        return _to_number_data(self.raw_data, self._option_mapping("n2t"))

    @property
    def text_data(self) -> dict[str, list]:
        return _to_text_data(self.raw_data, self._option_mapping("n2t"))

    def get_df(self, dtype: Literal["number", "text"]) -> pl.DataFrame:
        data = self.text_data if dtype == "text" else self.number_data
        return pl.DataFrame({**{Identifier.Id: self.response_ids, **data}})

    def describe(self) -> pl.DataFrame:
        df = self.get_df(dtype="number")

        describe_df = (
            df.unpivot(index=Identifier.Id, variable_name=self.id)
            .filter(pl.col("value"))
            .group_by(self.id)
            .agg(pl.n_unique(Identifier.Id).alias("count"))
            .with_columns(
                (pl.col("count") / pl.sum("count")).alias("percent"),
                (pl.col("count") / pl.sum("count")).cum_sum().alias("cum_percent"),
            )
        )

        return describe_df
