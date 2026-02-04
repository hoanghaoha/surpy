import polars as pl

from .strategy import QuestionStrategy
from ..option import Option
from ...errors import DataError


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

        if len(data) != len(self.response_ids):
            raise DataError("Lenght of data is different with length of response_ids")

        if 1 not in data.keys():
            raise DataError("Single question data must have 1 in keys")

        self.data = data[1]

    @property
    def dtype(self) -> str:
        if any([isinstance(d, (int, float)) for d in self.data]):
            return "number"
        return "text"

    def get_df(self) -> pl.DataFrame: ...

    def describe(self) -> pl.DataFrame: ...
