import polars as pl

from .strategy import QuestionStrategy
from ..option import Option


class MatrixMultipleStrategy(QuestionStrategy):
    def __init__(
        self,
        **kwargs,
    ) -> None:
        self.id: str = kwargs["id"]
        self.text: str = kwargs["text"]
        self.options: list[Option] = kwargs["options"]
        self.data: dict = kwargs["data"]
        self.response_ids: dict = kwargs["response_ids"]

    def _validate_data(self, data: dict) -> None: ...

    @property
    def dtype(self) -> str: ...

    def get_df(self) -> pl.DataFrame: ...

    def describe(self) -> pl.DataFrame: ...
