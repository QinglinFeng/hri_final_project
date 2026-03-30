"""End-to-end tests for the version space learning pipeline.

These tests verify that the learner:
- Narrows the version space correctly as examples are given
- Converges to the true concept with enough examples
- F1 score improves over time
- Active learning queries are more efficient than random labeling
- All four study concepts (HOUSE, SNOWMAN, ALIEN, ICE CREAM) can be learned
"""

import random

from hri_final_project.compound_object import (
    CompoundObject,
    generate_instance_space,
    matches_hypothesis,
)
from hri_final_project.version_space import CONCEPTS, VersionSpaceLearner


# ── Helpers ──────────────────────────────────────────────────────────────────


def _label(obj: CompoundObject, concept: str) -> bool:
    """Return the true label for an object under a concept."""
    return matches_hypothesis(obj, CONCEPTS[concept])


def _teach_with_random_examples(
    concept: str, n_examples: int, seed: int = 42
) -> VersionSpaceLearner:
    """Teach a learner with stratified random examples (half pos, half neg).

    Pure random sampling almost never hits positives for sparse concepts like
    HOUSE (~3% of instances), so we explicitly balance the sample.
    """
    rng = random.Random(seed)
    space = generate_instance_space()
    positives = [obj for obj in space if _label(obj, concept)]
    negatives = [obj for obj in space if not _label(obj, concept)]

    n_pos = max(1, n_examples // 2)
    n_neg = n_examples - n_pos
    chosen = rng.sample(positives, min(n_pos, len(positives))) + rng.sample(
        negatives, min(n_neg, len(negatives))
    )
    rng.shuffle(chosen)

    learner = VersionSpaceLearner(true_concept=concept)
    for obj in chosen:
        learner.update(obj, _label(obj, concept))
    return learner


def _teach_with_active_queries(
    concept: str, n_examples: int
) -> VersionSpaceLearner:
    """Teach a learner using active learning (query-by-committee)."""
    space = generate_instance_space()
    learner = VersionSpaceLearner(true_concept=concept)
    current = space[0]
    learner.update(current, _label(current, concept))

    for _ in range(n_examples - 1):
        query = learner.get_best_query(current)
        if query is None:
            break  # converged
        learner.update(query, _label(query, concept))
        current = query

    return learner


# ── VS size tests ─────────────────────────────────────────────────────────────


def test_vs_shrinks_with_positive_examples() -> None:
    """VS should shrink after each informative positive example."""
    learner = VersionSpaceLearner(true_concept="HOUSE")
    space = generate_instance_space()
    positives = [obj for obj in space if _label(obj, "HOUSE")]

    prev_size = learner.version_space_size
    for obj in positives[:5]:
        learner.update(obj, True)
        assert learner.version_space_size <= prev_size
        prev_size = learner.version_space_size


def test_vs_shrinks_with_negative_examples() -> None:
    """VS should shrink after each informative negative example."""
    learner = VersionSpaceLearner(true_concept="HOUSE")
    space = generate_instance_space()
    negatives = [obj for obj in space if not _label(obj, "HOUSE")]

    prev_size = learner.version_space_size
    for obj in negatives[:5]:
        learner.update(obj, False)
        assert learner.version_space_size <= prev_size
        prev_size = learner.version_space_size


def test_vs_never_goes_negative() -> None:
    """VS size should always be >= 1."""
    learner = VersionSpaceLearner(true_concept="HOUSE")
    space = generate_instance_space()
    for obj in space[:30]:
        learner.update(obj, _label(obj, "HOUSE"))
        assert learner.version_space_size >= 1


# ── F1 score tests ────────────────────────────────────────────────────────────


def test_f1_improves_over_examples() -> None:
    """F1 score should be higher after 10 examples than after 2."""
    learner_few = _teach_with_random_examples("HOUSE", n_examples=2)
    learner_more = _teach_with_random_examples("HOUSE", n_examples=10)

    f1_few = learner_few.current_accuracy or 0.0
    f1_more = learner_more.current_accuracy or 0.0
    assert f1_more >= f1_few, f"F1 did not improve: {f1_few:.3f} → {f1_more:.3f}"


def test_f1_above_zero_after_few_examples() -> None:
    """F1 should be above zero after a handful of examples."""
    for concept in CONCEPTS:
        learner = _teach_with_random_examples(concept, n_examples=5)
        f1 = learner.current_accuracy or 0.0
        assert f1 > 0.0, f"F1 is 0 for {concept} after 5 examples"


# ── Convergence tests ─────────────────────────────────────────────────────────


def test_house_converges_with_enough_examples() -> None:
    """HOUSE concept should reach F1 >= 0.8 with 20 random examples."""
    learner = _teach_with_random_examples("HOUSE", n_examples=20)
    f1 = learner.current_accuracy or 0.0
    assert f1 >= 0.8, f"HOUSE did not converge: F1={f1:.3f}"


def test_all_concepts_learn() -> None:
    """All four concepts should reach F1 > 0.5 with 15 random examples."""
    for concept in CONCEPTS:
        learner = _teach_with_random_examples(concept, n_examples=15)
        f1 = learner.current_accuracy or 0.0
        assert f1 > 0.5, f"{concept} failed to learn: F1={f1:.3f}"


# ── Active learning efficiency test ──────────────────────────────────────────


def test_active_learning_shrinks_vs_faster() -> None:
    """Active learning should shrink the VS faster than passive labeling.

    Both learners receive the same first positive example. The active learner
    then picks queries that maximally split the VS; the passive learner just
    receives the same objects in a fixed order. After 10 total examples the
    active learner should have a smaller or equal VS.
    """
    concept = "HOUSE"
    space = generate_instance_space()
    positives = [obj for obj in space if _label(obj, concept)]
    negatives = [obj for obj in space if not _label(obj, concept)]

    # First example is a positive (same for both)
    first = positives[0]

    # Passive: label first positive, then 9 negatives in order
    passive = VersionSpaceLearner(true_concept=concept)
    passive.update(first, True)
    for obj in negatives[:9]:
        passive.update(obj, _label(obj, concept))

    # Active: label first positive, then follow active queries
    active = VersionSpaceLearner(true_concept=concept)
    active.update(first, True)
    current = first
    for _ in range(9):
        query = active.get_best_query(current)
        if query is None:
            break
        active.update(query, _label(query, concept))
        current = query

    assert active.version_space_size <= passive.version_space_size, (
        f"Active VS ({active.version_space_size}) larger than passive "
        f"({passive.version_space_size})"
    )


# ── Prediction tests ──────────────────────────────────────────────────────────


def test_prediction_matches_true_label_after_convergence() -> None:
    """After many examples, predictions should match the true concept."""
    learner = _teach_with_random_examples("HOUSE", n_examples=40)
    space = generate_instance_space()
    sample = space[:20]

    correct = 0
    for obj in sample:
        pred, _ = learner.predict_label(obj)
        if pred == _label(obj, "HOUSE"):
            correct += 1

    accuracy = correct / len(sample)
    assert accuracy >= 0.7, f"Prediction accuracy too low: {accuracy:.2f}"


def test_query_always_differs_by_one_piece() -> None:
    """Every active query must differ from the current object by exactly one piece."""
    learner = VersionSpaceLearner(true_concept="SNOWMAN")
    space = generate_instance_space()
    current = space[0]
    learner.update(current, _label(current, "SNOWMAN"))

    for obj in space[1:10]:
        learner.update(obj, _label(obj, "SNOWMAN"))
        query = learner.get_best_query(current)
        if query is not None:
            assert current.differs_by_one_piece(query), (
                f"Query does not differ by one piece from current"
            )
        current = obj
