import polars as pl
import yaml

from ..errors import FileTypeError, DataError
from ..questions.question import Question
from ..questions.option import Option


class Survey:
    def __init__(self, questions: list[Question]):
        self.questions = questions


class SurveyBuilder:
    def __init__(self, data_path: str, metadata_path: str):
        self.data_path = data_path
        self.metadata_path = metadata_path

    def build(self) -> Survey:
        if self.data_path.endswith("xlsx"):
            return self._build_excel()
        if self.data_path.endswith("json"):
            return self._build_json()

        raise FileTypeError(
            f"Can not identify file type: {self.data_path.split('.')[-1]}"
        )

    def _build_excel(self) -> Survey:
        data_dict = self._process_excel_data()
        metadata_dict = self._process_metadata()

        questions = [
            Question(
                id=id,
                qtype=metadata["type"],
                text=metadata["text"],
                options=[
                    Option(question_id=id, index=i, text=op)
                    for i, op in enumerate(metadata["options"], 1)
                ],
                data=data_dict[id],
                response_ids=data_dict["ID"],
            )
            for id, metadata in metadata_dict.items()
        ]

        return Survey(questions=questions)

    def _build_json(self) -> Survey:
        return Survey([])

    def _process_excel_data(self) -> dict:
        """
        Return dictionary with id as key and data as value.
        {"ID": ["001", "002", "003"], "Q1": [1, 2, 4]}, "Q2": [[1, 0, 1], [0, 1, 0]]}
        """

        rawdata = pl.read_excel(self.data_path)

        if "ID" not in rawdata.columns:
            raise DataError("Could not find ID variable")

        return {}

    def _process_metadata(self) -> dict:
        """
        Return a dictionary with id as key and metadata as value.
        {"Q1": {"text": "question 1", options: []}
        """

        metadata = yaml.safe_load(self.metadata_path)

        return {question_info[id]: question_info for question_info in metadata}
