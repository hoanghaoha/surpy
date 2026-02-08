from typing import Literal
import polars as pl

from .strategy import QuestionStrategy
from ..option import Option
from ...errors import DataError
from ...config import Identifier


def _validate_data(data: dict, response_ids: list) -> None:
    if 1 not in data:
        raise DataError("Single question data must have 1 in keys")

    if len(data) != 1:
        raise DataError("Single question data can only have one key")

    values = data[1]

    if len(values) != len(response_ids):
        raise DataError("Length mismatch")

    if not all(isinstance(d, (str, int, type(None))) for d in values):
        raise DataError("Invalid data type")


def _to_number_data(
    data: list[str | int | float | None], option_mapping: dict[str, int]
) -> list[int | None]:
    if all([isinstance(d, (int, float, type(None))) for d in data]):
        return [int(d) if d is not None else None for d in data]
    return [
        {**option_mapping, **{"None": None, "": None}}.get(d, None)
        for d in [str(d) for d in data]
    ]


def _to_text_data(
    data: list[int | None], option_mapping: dict[int, str]
) -> list[str | None]:
    number_data: list[int] = [int(d) if d is not None else 0 for d in data]
    return [{**option_mapping, **{0: ""}}.get(d, "") for d in number_data]


class SingleStrategy(QuestionStrategy):
    def __init__(
        self,
        **kwargs,
    ) -> None:
        self.id: str = kwargs["id"]
        self.text: str = kwargs["text"]
        self.options: list[Option] = kwargs["options"]
        self.response_ids: list = kwargs["response_ids"]
        _validate_data(kwargs["data"], self.response_ids)
        self.raw_data: list[str | int | float | None] = kwargs["data"][1]

    def _option_mapping(self, _type: Literal["t2n", "n2t"]) -> dict:
        if _type == "t2n":
            return {op.text: op.index for op in self.options}
        return {op.index: op.text for op in self.options}

    @property
    def number_data(self) -> list[int | None]:
        return _to_number_data(self.raw_data, self._option_mapping("t2n"))

    @property
    def text_data(self):
        return _to_text_data(self.number_data, self._option_mapping("n2t"))

    def get_df(self, dtype: Literal["number", "text"]) -> pl.DataFrame:
        return pl.DataFrame(
            {
                Identifier.Id: self.response_ids,
                self.id: self.text_data if dtype == "text" else self.number_data,
            }
        )

    def describe(self) -> pl.DataFrame:
        df = self.get_df(dtype="text")

        describe_df = (
            df.group_by(self.id)
            .agg(
                pl.n_unique(Identifier.Id).alias("count"),
            )
            .sort(pl.col(self.id).replace(self._option_mapping("t2n")))
            .with_columns(
                (pl.col("count") / pl.sum("count")).alias("percent"),
                (pl.col("count") / pl.sum("count")).cum_sum().alias("cum_percent"),
            )
            .cast(
                {
                    self.id: pl.String,
                    "count": pl.UInt32,
                    "percent": pl.Float64,
                    "cum_percent": pl.Float64,
                }
            )
        )

        return describe_df
