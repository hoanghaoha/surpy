import polars as pl
import json
import yaml
from pathlib import Path
from functools import partial

from .survey import Survey
from ..errors import FilePathError, DataError
from ..questions.question import Question
from ..questions.option import Option
from ..config import Identifier


def _load_data_single(survey_data: dict, question_code: str, question_data: list):
    question_id = question_code

    if question_id in survey_data:
        raise ValueError("Duplicate question code")

    survey_data[question_id] = {1: question_data}


def _load_data_multiple(survey_data: dict, question_code: str, question_data: list):
    try:
        question_id, multiple_index = question_code.split(Identifier.Multiple)
        multiple_index = int(multiple_index)
    except Exception as e:
        raise ValueError(f"Invalid question code: {question_code}") from e

    survey_data.setdefault(question_id, {})

    if not isinstance(survey_data[question_id], dict):
        raise TypeError(f"survey_data[{question_id}] must a a dict")

    if multiple_index in survey_data[question_id]:
        raise ValueError("Duplicate multiple index")

    survey_data[question_id][multiple_index] = question_data


def _load_data_matrix_single(
    survey_data: dict, question_code: str, question_data: list
):
    try:
        question_id, matrix_index = question_code.split(Identifier.Matrix)
        matrix_index = int(matrix_index)
    except Exception as e:
        raise ValueError(f"Invalid question code: {question_code}") from e

    survey_data.setdefault(question_id, {})

    if not isinstance(survey_data[question_id], dict):
        raise TypeError(f"survey_data[{question_id}] must a a dict")

    if matrix_index in survey_data[question_id]:
        raise ValueError("Duplicate matrix index")

    survey_data[question_id][matrix_index] = question_data


def _load_data_matrix_multiple(
    survey_data: dict, question_code: str, question_data: list
):
    try:
        question_id, sub_question_code = question_code.split(Identifier.Matrix)
        matrix_index, multiple_index = sub_question_code.split(Identifier.Multiple)
        matrix_index, multiple_index = int(matrix_index), int(multiple_index)
    except Exception as e:
        raise ValueError(f"Invalid question code: {question_code}") from e

    survey_data.setdefault(question_id, {})
    survey_data[question_id].setdefault(matrix_index, {})

    if not isinstance(survey_data[question_id], dict):
        raise TypeError(f"survey_data[{question_id}] must a a dict")

    if not isinstance(survey_data[question_id][matrix_index], dict):
        raise TypeError(f"survey_data[{question_id}][{matrix_index}] must a a dict")

    if multiple_index in survey_data[question_id][matrix_index]:
        raise ValueError("Duplicate matrix/ multiple index")

    survey_data[question_id][matrix_index][multiple_index] = question_data


def _load_data_rank(survey_data: dict, question_code: str, question_data: list):
    try:
        question_id, rank_index = question_code.split(Identifier.Rank)
        rank_index = int(rank_index)
    except Exception as e:
        raise ValueError(f"Invalid question code: {question_code}") from e

    survey_data.setdefault(question_id, {})

    if rank_index in survey_data[question_id]:
        raise ValueError("Duplicate rank index")

    survey_data[question_id][rank_index] = question_data


def _load_survey_data(raw_data: dict[str, list]) -> dict[str, dict]:
    if Identifier.Id not in raw_data.keys():
        raise DataError("Could not find ID")

    survey_data = {}

    for column, column_data in raw_data.items():
        if Identifier.Multiple in column and Identifier.Matrix not in column:
            _load_data_multiple(survey_data, column, column_data)
        elif Identifier.Multiple not in column and Identifier.Matrix in column:
            _load_data_matrix_single(survey_data, column, column_data)
        elif Identifier.Multiple in column and Identifier.Matrix in column:
            _load_data_matrix_multiple(survey_data, column, column_data)
        elif Identifier.Rank in column:
            _load_data_rank(survey_data, column, column_data)
        else:
            _load_data_single(survey_data, column, column_data)

    return survey_data


def _load_excel_data(
    path: Path, sheet_name: str | None = None
) -> dict[str, dict[int, list]]:
    if sheet_name:
        raw_data: dict[str, list] = pl.read_excel(path, sheet_name=sheet_name).to_dict(
            as_series=False
        )
    else:
        raw_data: dict[str, list] = pl.read_excel(path).to_dict(as_series=False)

    return _load_survey_data(raw_data)


def _load_csv_data(path: Path) -> dict[str, dict[int, list]]:
    raw_data: dict[str, list] = pl.read_csv(path).to_dict(as_series=False)

    return _load_survey_data(raw_data)


def _load_json_data(path: Path) -> dict[str, dict[int, list]]:
    with open(path, "r") as f:
        raw_data = json.load(f)
        return _load_survey_data(raw_data)


def _load_yml_metadata(path: Path) -> dict[str, str | list]:
    with open(path, "r") as f:
        metasurvey_data = yaml.safe_load(f)
        return metasurvey_data


def _load_json_metadata(path: Path) -> dict[str, str | list]:
    with open(path, "r") as f:
        metasurvey_data = json.load(f)
        return metasurvey_data


class SurveyBuilder:
    def __init__(
        self, data_path: str, metadata_path: str, sheet_name: str | None = None
    ) -> None:
        self.data_path = Path(data_path)
        self.metadata_path = Path(metadata_path)
        self.sheet_name = sheet_name

    def build(self) -> Survey:
        data = self._load_data()
        survey_metadata = self._load_metadata()
        questions = [
            Question(
                id := question_metadata["id"],
                qtype=question_metadata["type"],
                text=question_metadata["text"],
                options=[
                    Option(index=i, text=op)
                    for i, op in enumerate(question_metadata.get("options", []), 1)
                ],
                data=data[id],
                response_ids=data[Identifier.Id][1],
            )
            for question_metadata in survey_metadata["questions"]
        ]

        return Survey(name=survey_metadata.get("name", "SURVEY"), questions=questions)

    def _load_data(self) -> dict[str, dict[int, list]]:
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

        _load_data_by_type = {
            ".csv": _load_csv_data,
            ".xlsx": partial(_load_excel_data, sheet_name=self.sheet_name),
            ".json": _load_json_data,
        }

        if self.data_path.exists():
            return _load_data_by_type[self.data_path.suffix](self.data_path)
        else:
            raise FilePathError(f"File does not exists: {self.data_path}")

    def _load_metadata(self) -> dict:
        """
        Return a dictionary with id as key and metadata as value.
        {"name": "test_survey", "questions": [{"id": "Q1", "type": "single_choice", "text": "question 1", "options": ["A", "B", "C"]}]}
        """

        _load_metadata_by_type = {
            ".yml": _load_yml_metadata,
            ".json": _load_json_metadata,
        }

        if self.metadata_path.exists():
            return _load_metadata_by_type[self.metadata_path.suffix](self.metadata_path)
        else:
            raise FilePathError(f"File does not exists: {self.metadata_path}")
