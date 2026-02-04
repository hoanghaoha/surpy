import polars as pl
import json
import yaml

from .survey import Survey
from ..errors import FileTypeError, DataError
from ..questions.question import Question
from ..questions.option import Option
from ..config import Identifier


def _load_data_single(data_dict: dict, var: str, data: list):
    data_dict[var] = {1: data}


def _load_data_multiple(data_dict: dict, var: str, data: list):
    root_var, var_index = var.split(Identifier.Multiple)
    data_dict.setdefault(root_var, {})
    data_dict[root_var][int(var_index)] = data


def _load_data_matrix_single(data_dict: dict, var: str, data: list):
    root_var, var_index = var.split(Identifier.Matrix)
    data_dict.setdefault(root_var, {})
    data_dict[root_var][int(var_index)] = data


def _load_data_matrix_multiple(data_dict: dict, var: str, data: list):
    root_var, sub_var = var.split(Identifier.Matrix)
    matrix_index, multiple_index = sub_var.split(Identifier.Multiple)
    data_dict.setdefault(root_var, {})
    data_dict[root_var].setdefault(matrix_index, {})
    data_dict[root_var][int(matrix_index)][int(multiple_index)] = data


def _load_data_rank(data_dict: dict, var: str, data: list):
    root_var, var_index = var.split(Identifier.Rank)
    data_dict.setdefault(root_var, {})
    data_dict[root_var][int(var_index)] = data


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
                response_ids=data_dict[Identifier.Id][1],
            )
            for id, metadata in metadata_dict.items()
        ]

        return Survey(questions=questions)

    def _load_excel_data(self) -> dict[str, dict]:
        """
        Return dictionary with id as key and data as value.
        {
            "Q1": {1: [1, 2, 3, 2],},
            "Q2": {
                1: [0, 1, 0, 0],
                2: [1, 0, 0, 1],
            },
            "Q3": {
                1: [1, 2, 3, 4],
                2: [3, 4, 2 1],
            },
            "Q4": {
                1: {
                    1: [0, 0, 1, 0],
                    2: [0, 1, 0, 1],
                },
                2: {
                    1: [1, 1, 1, 0],
                    2: [1, 0, 0, 1],
                }
            }
        }
        """

        raw_dict = pl.read_excel(self.data_path).to_dict(as_series=False)

        if Identifier.Id not in raw_dict.keys():
            raise DataError("Could not find ID variable")

        data_dict = {}

        for var, var_data in raw_dict.items():
            if Identifier.Multiple in var and Identifier.Matrix not in var:
                _load_data_multiple(data_dict, var, var_data)
            elif Identifier.Multiple not in var and Identifier.Matrix in var:
                _load_data_matrix_single(data_dict, var, var_data)
            elif Identifier.Multiple in var and Identifier.Matrix in var:
                _load_data_matrix_multiple(data_dict, var, var_data)
            elif Identifier.Rank in var:
                _load_data_rank(data_dict, var, var_data)
            else:
                _load_data_single(data_dict, var, var_data)

        return data_dict

    def _load_metadata(self) -> dict[str, dict]:
        """
        Return a dictionary with id as key and metadata as value.
        {"Q1": {"id": "Q1", "type": "single_choice", "text": "question 1", "options": ["A", "B", "C"]}
        """

        with open(self.metadata_path, "r") as f:
            if self.metadata_path.endswith(".yml"):
                metadata = yaml.safe_load(f)
            elif self.metadata_path.endswith(".json"):
                metadata = json.load(f)
            else:
                raise DataError(
                    f"Can not identify metadata type: {self.metadata_path.split('.')[-1]}"
                )

        return {
            question_info[id]: question_info for question_info in metadata["questions"]
        }

    def _build_json(self) -> Survey:
        return Survey([])
