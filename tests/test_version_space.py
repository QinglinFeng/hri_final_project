"""Tests for the version space learner."""

from hri_final_project.compound_object import (
    CompoundObject,
    generate_instance_space,
    matches_hypothesis,
)
from hri_final_project.version_space import CONCEPTS, VersionSpaceLearner


def _make_obj(
    ct: str, st: str, sit: str, cb: str, sb: str, sib: str
) -> CompoundObject:
    return CompoundObject(
        color_top=ct,
        shape_top=st,
        size_top=sit,
        color_bottom=cb,
        shape_bottom=sb,
        size_bottom=sib,
    )


def test_instance_space_size() -> None:
    """Instance space should contain exactly 552 objects."""
    space = generate_instance_space()
    assert len(space) == 552


def test_hypothesis_space_size() -> None:
    """Hypothesis space should contain 3600 hypotheses."""
    from hri_final_project.version_space import _generate_hypothesis_space  # noqa: PLC0415

    hs = _generate_hypothesis_space()
    assert len(hs) == 3600


def test_house_concept_positive() -> None:
    """A pink triangle on top of a square should be HOUSE-positive."""
    house = _make_obj("pink", "triangle", "small", "green", "square", "large")
    assert matches_hypothesis(house, CONCEPTS["HOUSE"])


def test_house_concept_negative() -> None:
    """A green triangle on top of a square is NOT a HOUSE (wrong color)."""
    not_house = _make_obj("green", "triangle", "small", "green", "square", "large")
    assert not matches_hypothesis(not_house, CONCEPTS["HOUSE"])


def test_version_space_update_positive() -> None:
    """After one positive example, VS size should decrease."""
    learner = VersionSpaceLearner(true_concept="HOUSE")
    initial_size = learner.version_space_size
    house = _make_obj("pink", "triangle", "small", "green", "square", "large")
    learner.update(house, True)
    assert learner.version_space_size < initial_size


def test_version_space_update_narrows() -> None:
    """Three HOUSE examples should narrow the VS significantly."""
    learner = VersionSpaceLearner(true_concept="HOUSE")
    examples = [
        (_make_obj("pink", "triangle", "small", "green", "square", "large"), True),
        (_make_obj("pink", "triangle", "large", "orange", "square", "small"), True),
        (_make_obj("green", "circle", "small", "orange", "circle", "large"), False),
    ]
    for obj, label in examples:
        learner.update(obj, label)
    assert learner.version_space_size < 3600
    assert learner.labeled_examples_count == 3


def test_predict_label_returns_valid_confidence() -> None:
    """Confidence should be in [0, 1]."""
    learner = VersionSpaceLearner()
    obj = _make_obj("pink", "triangle", "small", "green", "square", "large")
    _, confidence = learner.predict_label(obj)
    assert 0.0 <= confidence <= 1.0


def test_query_differs_by_one_piece() -> None:
    """Best query must differ from current example by exactly one piece."""
    learner = VersionSpaceLearner(true_concept="HOUSE")
    # Add a positive example to make the VS non-trivial but not converged
    house = _make_obj("pink", "triangle", "small", "green", "square", "large")
    learner.update(house, True)

    current = _make_obj("pink", "triangle", "small", "orange", "circle", "small")
    query = learner.get_best_query(current)

    if query is not None:
        assert current.differs_by_one_piece(query)


def test_noise_tolerance() -> None:
    """A mislabeled example should not collapse the version space."""
    learner = VersionSpaceLearner(true_concept="HOUSE")
    house = _make_obj("pink", "triangle", "small", "green", "square", "large")
    # Correct label
    learner.update(house, True)
    # Mislabel the same object
    learner.update(house, False)
    # VS should not be empty — relaxed consistency handles noise
    assert learner.version_space_size > 0
    # VS may be smaller or same, but should not be zero
    assert learner.labeled_examples_count == 2


def test_is_informative() -> None:
    """Before any updates, the full VS should make most objects informative."""
    learner = VersionSpaceLearner()
    obj = _make_obj("pink", "triangle", "small", "green", "square", "large")
    # With all hypotheses in VS, any non-trivial object should split
    assert learner.is_informative(obj)
