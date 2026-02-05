from typing import Literal
import polars as pl

from .strategy import QuestionStrategy
from ..option import Option
from ...errors import DataError
from ...config import Identifier


class SingleStrategy(QuestionStrategy):
    def __init__(
        self,
        **kwargs,
    ) -> None:
        self.id: str = kwargs["id"]
        self.text: str = kwargs["text"]
        self.options: list[Option] = kwargs["options"]
        self.response_ids: dict = kwargs["response_ids"]
        self._validate_data(kwargs["data"])

    def _validate_data(self, data: dict) -> None:
        if len(data) > 1:
            raise DataError(
                f"Length of Single question data can not be larger than 1: {self.id} is {len(data)}"
            )

        if len(data[1]) != len(self.response_ids):
            raise DataError("Lenght of data is different with length of response_ids")

        if 1 not in data.keys():
            raise DataError("Single question data must have 1 in keys")

        if not all([isinstance(d, (str, int)) for d in self.data]):
            raise DataError("Single question data must be int or str")

        self.data: list[str | int | None] = data[1]

    @property
    def dtype(self) -> Literal["number", "text"]:
        if all([isinstance(d, int) or d is None for d in self.data]):
            return "number"
        return "text"

    @property
    def _t2n(self) -> dict[str, int]:
        return {op.text: op.index for op in self.options}

    @property
    def _n2t(self) -> dict[int, str]:
        return {op.index: op.text for op in self.options}

    def change_dtype(self, to: Literal["number", "text"]):
        if self.dtype == "text" and to == "number":
            str_data: list[str] = [str(d) for d in self.data]
            self.data = [{**self._t2n, **{"None": None}}.get(d, None) for d in str_data]
        if self.dtype == "number" and to == "text":
            number_data: list[int] = [int(d) if d is not None else 0 for d in self.data]
            self.data = [{**self._n2t, **{0: None}}.get(d, None) for d in number_data]

    def get_df(self) -> pl.DataFrame:
        return pl.DataFrame({self.id: self.data, Identifier.Id: self.response_ids})

    def describe(self) -> pl.DataFrame:
        current_dtype = self.dtype

        if current_dtype == "number":
            self.change_dtype("text")

        df = self.get_df()

        self.change_dtype(current_dtype)

        describe_df = (
            df.group_by(self.id)
            .agg(
                pl.n_unique(Identifier.Id).alias("count"),
            )
            .sort(pl.col(self.id).replace(self._t2n))
            .with_columns(
                (pl.col("count") / pl.sum("count")).alias("percent"),
                (pl.col("count") / pl.sum("count")).cum_sum().alias("cum_percent"),
            )
        )

        return describe_df
