from typing import Literal
import polars as pl

from ...errors import DataError
from ..option import Option
from .strategy import QuestionStrategy
from ...config import Identifier


class MultipleStrategy(QuestionStrategy):
    def __init__(
        self,
        **kwargs,
    ) -> None:
        self.id: str = kwargs["id"]
        self.text: str = kwargs["text"]
        self.options: list[Option] = kwargs["options"]
        self.response_ids: dict = kwargs["response_ids"]
        self._validate_data(kwargs["data"])

    def _validate_data(self, data: dict[int, list]) -> None:
        if len(data) != len(self.options):
            raise DataError(
                "Length of Multiple question must be equal to length of Multiple question options."
            )
        if not all([len(v) != len(self.response_ids) for v in data.values()]):
            raise DataError(
                "Length of Multiple question data must be equal to lenght of response ids."
            )
        if not all([isinstance(k, int) for k in data.keys()]):
            raise DataError("Key of Multiple question must be integer.")

        sorted_data = dict(sorted(data.items(), key=lambda x: x[0]))

        self.data: dict[str, list[str | int | None]] = {
            {op.index: op.text for op in self.options}[op_index]: [
                1 if d else 0 for d in op_data
            ]
            for op_index, op_data in sorted_data.items()
        }

    @property
    def dtype(self) -> Literal["number", "text"]:
        if all([isinstance(d, int) for var in self.data.values() for d in var]):
            return "number"
        return "text"

    def get_option(self, value: int | str):
        if isinstance(value, int):
            return {op.index: op for op in self.options}[value]
        if isinstance(value, str):
            return {op.text: op for op in self.options}[value]

    def change_dtype(self, to: Literal["number", "text"]):
        if self.dtype == "text" and to == "number":
            self.data = {
                op_text: [1 if d else 0 for d in op_data]
                for op_text, op_data in self.data.items()
            }
        if self.dtype == "number" and to == "text":
            self.data = {
                op_text: [op_text if d else "" for d in op_data]
                for op_text, op_data in self.data.items()
            }

    def get_df(self) -> pl.DataFrame:
        return pl.DataFrame({**{Identifier.Id: self.response_ids, **self.data}})

    def describe(self) -> pl.DataFrame:
        current_dtype = self.dtype

        if current_dtype == "number":
            self.change_dtype("text")

        df = self.get_df()

        self.change_dtype(current_dtype)

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
