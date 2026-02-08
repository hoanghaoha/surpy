from pathlib import Path
from surpy.survey.survey_builder import SurveyBuilder


FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_build_survey():
    survey_builder = SurveyBuilder(
        data_path=str(FIXTURES / "survey_data.xlsx"),
        metadata_path=str(FIXTURES / "survey_metadata.yml"),
        sheet_name="text",
    )

    survey = survey_builder.build()

    assert len(survey.questions) == 8
