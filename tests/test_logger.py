"""Tests for ExperimentLogger."""

import json
import tempfile
from pathlib import Path

from hri_final_project.compound_object import CompoundObject
from hri_final_project.logger import ExperimentLogger


def _make_obj(
    ct: str = "pink",
    st: str = "triangle",
    sit: str = "small",
    cb: str = "green",
    sb: str = "square",
    sib: str = "large",
) -> CompoundObject:
    return CompoundObject(
        color_top=ct,
        shape_top=st,
        size_top=sit,
        color_bottom=cb,
        shape_bottom=sb,
        size_bottom=sib,
    )


def _read_log(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_log_creates_file() -> None:
    """Logger should create the log file on first write."""
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "logs" / "test.jsonl"
        logger = ExperimentLogger(log_path)
        assert not log_path.exists()

        logger.log(
            subject_id="p01",
            mode="SL",
            concept="HOUSE",
            interaction_step=1,
            current_example=_make_obj(),
            sentence_type="positive_label",
            current_label=True,
            answer_type="acknowledge",
            query=None,
            version_space_size=3600,
            is_informative=True,
        )
        assert log_path.exists()


def test_log_writes_valid_json() -> None:
    """Each log entry should be valid JSON."""
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "test.jsonl"
        logger = ExperimentLogger(log_path)
        logger.log(
            subject_id="p01",
            mode="SL",
            concept="HOUSE",
            interaction_step=1,
            current_example=_make_obj(),
            sentence_type="positive_label",
            current_label=True,
            answer_type="acknowledge",
            query=None,
            version_space_size=3600,
            is_informative=True,
        )
        records = _read_log(log_path)
        assert len(records) == 1


def test_log_contains_required_fields() -> None:
    """Each record should contain all required fields."""
    required = {
        "subject_id",
        "mode",
        "concept",
        "system_time",
        "interaction_step",
        "current_example",
        "sentence_type",
        "current_label",
        "answer_type",
        "query",
        "version_space_size",
        "is_informative",
    }
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "test.jsonl"
        logger = ExperimentLogger(log_path)
        logger.log(
            subject_id="p01",
            mode="AL",
            concept="SNOWMAN",
            interaction_step=3,
            current_example=_make_obj(),
            sentence_type="test_question",
            current_label=None,
            answer_type="answer",
            query=None,
            version_space_size=100,
            is_informative=False,
        )
        record = _read_log(log_path)[0]
        assert required.issubset(record.keys())


def test_log_appends_multiple_entries() -> None:
    """Multiple log calls should append to the same file."""
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "test.jsonl"
        logger = ExperimentLogger(log_path)
        for i in range(5):
            logger.log(
                subject_id="p01",
                mode="MI",
                concept="ALIEN",
                interaction_step=i,
                current_example=_make_obj(),
                sentence_type="positive_label",
                current_label=True,
                answer_type="acknowledge",
                query=None,
                version_space_size=3600 - i * 100,
                is_informative=True,
            )
        records = _read_log(log_path)
        assert len(records) == 5
        assert [r["interaction_step"] for r in records] == list(range(5))


def test_log_query_serialized_correctly() -> None:
    """When a query is present it should appear as a dict in the record."""
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "test.jsonl"
        logger = ExperimentLogger(log_path)
        query_obj = _make_obj(ct="orange", st="circle")
        logger.log(
            subject_id="p01",
            mode="AL",
            concept="HOUSE",
            interaction_step=2,
            current_example=_make_obj(),
            sentence_type="positive_label",
            current_label=True,
            answer_type="query",
            query=query_obj,
            version_space_size=500,
            is_informative=True,
        )
        record = _read_log(log_path)[0]
        assert isinstance(record["query"], dict)
        assert record["query"]["color_top"] == "orange"
        assert record["query"]["shape_top"] == "circle"


def test_log_null_query_serialized_as_none() -> None:
    """When no query, the query field should be null (None) in JSON."""
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "test.jsonl"
        logger = ExperimentLogger(log_path)
        logger.log(
            subject_id="p01",
            mode="SL",
            concept="HOUSE",
            interaction_step=1,
            current_example=_make_obj(),
            sentence_type="positive_label",
            current_label=True,
            answer_type="acknowledge",
            query=None,
            version_space_size=3600,
            is_informative=True,
        )
        record = _read_log(log_path)[0]
        assert record["query"] is None


def test_log_creates_parent_directories() -> None:
    """Logger should create nested directories if they don't exist."""
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "a" / "b" / "c" / "test.jsonl"
        logger = ExperimentLogger(log_path)
        logger.log(
            subject_id="p01",
            mode="AQ",
            concept="ICE CREAM",
            interaction_step=1,
            current_example=_make_obj(),
            sentence_type="end_session",
            current_label=None,
            answer_type=None,
            query=None,
            version_space_size=1,
            is_informative=False,
        )
        assert log_path.exists()
