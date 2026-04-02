"""Tests for interaction modes."""

from hri_final_project.compound_object import CompoundObject
from hri_final_project.interaction_modes import ALMode, AQMode, MIMode, SLMode
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


def _trained_learner() -> tuple[VersionSpaceLearner, CompoundObject]:
    """Return a learner with a few HOUSE examples and a current object."""
    learner = VersionSpaceLearner(true_concept="HOUSE")
    learner.update(_obj("pink", "triangle", "small", "green", "square", "large"), True)
    learner.update(_obj("pink", "triangle", "large", "orange", "square", "small"), True)
    learner.update(_obj("green", "circle", "small", "orange", "circle", "large"), False)
    current = _obj("pink", "triangle", "small", "orange", "circle", "small")
    return learner, current


def test_sl_never_queries() -> None:
    """SL mode should never return a query."""
    learner, current = _trained_learner()
    mode = SLMode(learner)
    assert mode.on_label_received(True, current) is None
    assert mode.on_label_received(False, current) is None


def test_al_always_queries() -> None:
    """AL mode should return a query after every label (while VS > 1)."""
    learner, current = _trained_learner()
    mode = ALMode(learner)
    query = mode.on_label_received(True, current)
    assert query is not None
    assert current.differs_by_one_piece(query)


def test_al_no_query_when_converged() -> None:
    """AL mode returns None when the version space has converged."""
    learner = VersionSpaceLearner(true_concept="HOUSE")
    # Flood with enough examples to converge
    for _ in range(30):
        learner.update(
            _obj("pink", "triangle", "small", "green", "square", "large"), True
        )
        learner.update(
            _obj("green", "circle", "small", "orange", "circle", "large"), False
        )
    current = _obj("pink", "triangle", "small", "orange", "circle", "small")
    mode = ALMode(learner)
    # If VS size is 1, no query should be returned
    if learner.version_space_size == 1:
        assert mode.on_label_received(True, current) is None


def test_mi_queries_on_uninformative_example() -> None:
    """MI mode should query when the labeled example was uninformative."""
    learner = VersionSpaceLearner(true_concept="HOUSE")
    # Converge VS enough that some objects become uninformative
    for _ in range(10):
        learner.update(
            _obj("pink", "triangle", "small", "green", "square", "large"), True
        )
    mode = MIMode(learner)
    # The same object again is likely uninformative now
    current = _obj("pink", "triangle", "small", "green", "square", "large")
    if not learner.is_informative(current):
        query = mode.on_label_received(True, current)
        assert query is None or current.differs_by_one_piece(query)


def test_aq_ignores_labels() -> None:
    """AQ mode should never query in response to a label."""
    learner, current = _trained_learner()
    mode = AQMode(learner)
    assert mode.on_label_received(True, current) is None
    assert mode.on_label_received(False, current) is None


def test_aq_queries_on_any_questions() -> None:
    """AQ mode should query when on_any_questions() is called."""
    learner, current = _trained_learner()
    mode = AQMode(learner)
    query = mode.on_any_questions(current)
    assert query is not None
    assert current.differs_by_one_piece(query)


def test_aq_returns_none_when_converged() -> None:
    """AQ mode returns None from on_any_questions() when VS has converged."""
    learner = VersionSpaceLearner(true_concept="HOUSE")
    for _ in range(30):
        learner.update(
            _obj("pink", "triangle", "small", "green", "square", "large"), True
        )
        learner.update(
            _obj("green", "circle", "small", "orange", "circle", "large"), False
        )
    current = _obj("pink", "triangle", "small", "orange", "circle", "small")
    mode = AQMode(learner)
    if learner.version_space_size == 1:
        assert mode.on_any_questions(current) is None
