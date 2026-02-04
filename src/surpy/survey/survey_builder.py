import polars as pl
import json
import yaml

from .survey import Survey
from ..errors import FileTypeError, DataError
from ..questions.question import Question
from ..questions.option import Option
from ..config import Seperator


def _load_data_single(data_dict: dict, var: str, data: list):
    data_dict[var] = data


def _load_data_multiple(data_dict: dict, var: str, data: list):
    root_var, sub_var = var.split(Seperator.Multiple)
    data_dict.setdefault(root_var, {})
    data_dict[root_var][sub_var] = data


def _load_data_matrix_single(data_dict: dict, var: str, data: list):
    root_var, sub_var = var.split(Seperator.Matrix)
    data_dict.setdefault(root_var, {})
    data_dict[root_var][sub_var] = data


def _load_data_matrix_multiple(data_dict: dict, var: str, data: list):
    root_var, sub_var = var.split(Seperator.Matrix)
    matrix_part, multiple_part = sub_var.split(Seperator.Multiple)
    data_dict.setdefault(root_var, {})
    data_dict[root_var].setdefault(matrix_part, {})
    data_dict[root_var][matrix_part][multiple_part] = data


def _load_data_rank(data_dict: dict, var: str, data: list):
    root_var, sub_var = var.split(Seperator.Rank)
    data_dict.setdefault(root_var, {})
    data_dict[root_var][sub_var] = data


class SurveyBuilder:
    def __init__(self, data_path: str, metadata_path: str):
        self.data_path = data_path
        self.metadata_path = metadata_path

    def build(self) -> Survey:
        if self.data_path.endswith(".xlsx"):
            return self._build_excel()
        if self.data_path.endswith(".json"):
            return self._build_json()

        raise FileTypeError(
            f"Can not identify file type: {self.data_path.split('.')[-1]}"
        )

    def _build_excel(self) -> Survey:
        data_dict = self._load_excel_data()
        metadata_dict = self._load_metadata()

        questions = [
            Question(
                id,
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

    def _load_excel_data(self) -> dict[str, dict]:
        """
        Return dictionary with id as key and data as value.
        {
            "Q1": [1, 2, 3, 2],
            "Q2": {
                "1": [0, 1, 0, 0],
                "2": [1, 0, 0, 1],
            },
            "Q3": {
                "1": [1, 2, 3, 4],
                "2": [3, 4, 2 1],
            },
            "Q4": {
                "1": {
                    "1": [0, 0, 1, 0],
                    "2": [0, 1, 0, 1],
                },
                "2": {
                    "1": [1, 1, 1, 0],
                    "2": [1, 0, 0, 1],
                }
            }
        }
        """

        raw_dict = pl.read_excel(self.data_path).to_dict(as_series=False)

        if "ID" not in raw_dict.keys():
            raise DataError("Could not find ID variable")

        data_dict = {}

        for var, var_data in raw_dict.items():
            if Seperator.Multiple in var and Seperator.Matrix not in var:
                _load_data_multiple(data_dict, var, var_data)
            elif Seperator.Multiple not in var and Seperator.Matrix in var:
                _load_data_matrix_single(data_dict, var, var_data)
            elif Seperator.Multiple in var and Seperator.Matrix in var:
                _load_data_matrix_multiple(data_dict, var, var_data)
            elif Seperator.Rank in var:
                _load_data_rank(data_dict, var, var_data)
            else:
                _load_data_single(data_dict, var, var_data)

        return data_dict

    def _load_metadata(self) -> dict[str, dict]:
        """
        Return a dictionary with id as key and metadata as value.
        {"Q1": {"text": "question 1", options: []}
        """

        with open(self.metadata_path, "r") as f:
            if self.metadata_path.endswith(".yml"):
                metadata = yaml.safe_load(f)
            elif self.metadata_path.endswith(".json"):
                metadata = json.load(f)
            else:
                raise DataError(
                    "Can not identify metadata type: {self.metadata_path.split('.')[-1]}"
                )

        return {
            question_info[id]: question_info for question_info in metadata["questions"]
        }

    def _build_json(self) -> Survey:
        return Survey([])
