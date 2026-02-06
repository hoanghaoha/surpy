from surpy.survey.survey import Survey
from unittest.mock import Mock


def test_survey_keep_questions():
    q1 = Mock()
    q2 = Mock()

    survey = Survey(questions=[q1, q2])

    assert survey.questions == [q1, q2]
