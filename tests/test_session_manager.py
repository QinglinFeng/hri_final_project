"""Integration tests for SessionManager using a mocked teacher interface."""

# pylint: disable=redefined-outer-name
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from hri_final_project.compound_object import CompoundObject
from hri_final_project.interaction_modes import ALMode, InteractionMode, SLMode
from hri_final_project.logger import ExperimentLogger
from hri_final_project.session_manager import SessionManager
from hri_final_project.version_space import VersionSpaceLearner


def _obj(ct: str, st: str, sit: str, cb: str, sb: str, sib: str) -> CompoundObject:
    return CompoundObject(
        color_top=ct,
        shape_top=st,
        size_top=sit,
        color_bottom=cb,
        shape_bottom=sb,
        size_bottom=sib,
    )


@pytest.fixture
def tmp_logger(tmp_path: Path) -> ExperimentLogger:
    """Create a temporary logger for tests."""
    return ExperimentLogger(tmp_path / "test.jsonl")


@pytest.fixture
def house_obj() -> CompoundObject:
    """Return a compound object matching the HOUSE concept."""
    return _obj("pink", "triangle", "small", "green", "square", "large")


@pytest.fixture
def non_house_obj() -> CompoundObject:
    """Return a compound object that does not match the HOUSE concept."""
    return _obj("green", "circle", "small", "orange", "circle", "large")


def _make_session(
    mode_name: str, tmp_logger: ExperimentLogger
) -> tuple[SessionManager, VersionSpaceLearner]:
    learner = VersionSpaceLearner(true_concept="HOUSE")
    mode: InteractionMode
    if mode_name == "SL":
        mode = SLMode(learner)
    else:
        mode = ALMode(learner)
    session = SessionManager(
        subject_id="test_subj",
        concept_name="HOUSE",
        mode_name=mode_name,
        mode=mode,
        learner=learner,
        logger=tmp_logger,
    )
    return session, learner


@patch("hri_final_project.session_manager.TeacherUtteranceParser")
def test_positive_label_updates_learner(
    mock_parser_class: MagicMock,
    tmp_logger: ExperimentLogger,
    house_obj: CompoundObject,
) -> None:
    """A positive label utterance should update the version space."""
    mock_parser_class.return_value.parse.return_value = {"type": "positive_label"}
    session, learner = _make_session("SL", tmp_logger)
    initial_vs = learner.version_space_size

    session.process_turn("Pepper, this is a HOUSE", house_obj)

    assert learner.version_space_size < initial_vs
    assert learner.labeled_examples_count == 1


@patch("hri_final_project.session_manager.TeacherUtteranceParser")
def test_negative_label_updates_learner(
    mock_parser_class: MagicMock,
    tmp_logger: ExperimentLogger,
    non_house_obj: CompoundObject,
) -> None:
    """A negative label utterance should update the version space."""
    mock_parser_class.return_value.parse.return_value = {"type": "negative_label"}
    session, learner = _make_session("SL", tmp_logger)

    session.process_turn("Pepper, this is not a HOUSE", non_house_obj)

    assert learner.labeled_examples_count == 1


@patch("hri_final_project.session_manager.TeacherUtteranceParser")
def test_test_question_returns_answer(
    mock_parser_class: MagicMock,
    tmp_logger: ExperimentLogger,
    house_obj: CompoundObject,
) -> None:
    """A test question should produce a robot answer response."""
    mock_parser_class.return_value.parse.return_value = {"type": "test_question"}
    session, _ = _make_session("SL", tmp_logger)

    session.process_turn("Pepper, is this a HOUSE?", house_obj)

    assert len(session.robot_response) > 0


@patch("hri_final_project.session_manager.TeacherUtteranceParser")
def test_end_session_deactivates(
    mock_parser_class: MagicMock,
    tmp_logger: ExperimentLogger,
    house_obj: CompoundObject,
) -> None:
    """An end_session utterance should deactivate the session."""
    mock_parser_class.return_value.parse.return_value = {"type": "end_session"}
    session, _ = _make_session("SL", tmp_logger)
    assert session.is_active

    session.process_turn("Pepper, we are done", house_obj)

    assert not session.is_active


@patch("hri_final_project.session_manager.TeacherUtteranceParser")
def test_al_mode_issues_query_after_label(
    mock_parser_class: MagicMock,
    tmp_logger: ExperimentLogger,
    house_obj: CompoundObject,
) -> None:
    """AL mode should include a query in the robot response after a label."""
    mock_parser_class.return_value.parse.return_value = {"type": "positive_label"}
    session, _ = _make_session("AL", tmp_logger)

    session.process_turn("Pepper, this is a HOUSE", house_obj)

    assert "replace" in session.robot_response.lower()


@patch("hri_final_project.session_manager.TeacherUtteranceParser")
def test_log_file_written(
    mock_parser_class: MagicMock,
    tmp_path: Path,
    house_obj: CompoundObject,
) -> None:
    """Events should be written to the log file."""
    mock_parser_class.return_value.parse.return_value = {"type": "positive_label"}
    log_path = tmp_path / "test.jsonl"
    logger = ExperimentLogger(log_path)
    session, _ = _make_session("SL", logger)

    session.process_turn("Pepper, this is a HOUSE", house_obj)

    assert log_path.exists()
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 1


@patch("hri_final_project.session_manager.TeacherUtteranceParser")
def test_status_line_format(
    mock_parser_class: MagicMock,  # pylint: disable=unused-argument
    tmp_logger: ExperimentLogger,
) -> None:
    """Status line should contain mode, concept, vs_size, examples."""
    session, _ = _make_session("AL", tmp_logger)
    status = session.status_line()
    assert "AL" in status
    assert "HOUSE" in status
    assert "vs_size" in status
    assert "examples" in status
