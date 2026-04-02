"""Version space learner as described in Algorithm 1 of Cakmak et al.

(2010).
"""

from itertools import product
from typing import Optional

from hri_final_project.compound_object import (
    FEATURE_VALUES,
    WILDCARD,
    CompoundObject,
    generate_instance_space,
    matches_hypothesis,
)

# A hypothesis is a dict mapping feature -> value (or WILDCARD).
# The full hypothesis space = all monotone conjunctions over feature-value pairs.
Hypothesis = dict[str, str]


def _generate_hypothesis_space() -> list[Hypothesis]:
    """Generate all possible monotone conjunctions (3600 total)."""
    feature_options = []
    for feature, values in FEATURE_VALUES.items():
        # Each feature can be WILDCARD or any of its values
        feature_options.append([(feature, WILDCARD)] + [(feature, v) for v in values])

    hypotheses = []
    for combo in product(*feature_options):
        h: Hypothesis = dict(combo)
        hypotheses.append(h)
    return hypotheses


# The four target concepts from the paper
CONCEPTS: dict[str, Hypothesis] = {
    "HOUSE": {
        "shape_top": "triangle",
        "color_top": "pink",
        "shape_bottom": "square",
    },
    "SNOWMAN": {
        "shape_top": "circle",
        "size_top": "small",
        "shape_bottom": "circle",
    },
    "ALIEN": {
        "shape_top": "circle",
        "color_top": "green",
        "color_bottom": "green",
    },
    "ICE CREAM": {
        "shape_top": "circle",
        "shape_bottom": "triangle",
        "color_bottom": "yellow",
    },
}


class VersionSpaceLearner:
    """Version space learner with relaxed consistency for noise tolerance."""

    def __init__(self, true_concept: Optional[str] = None) -> None:
        """Initialize the learner.

        Args:
            true_concept: Optional name of the true concept for accuracy tracking.
        """
        self._instance_space: list[CompoundObject] = generate_instance_space()
        self._hypothesis_space: list[Hypothesis] = _generate_hypothesis_space()
        self._consistency: list[int] = [0] * len(self._hypothesis_space)
        self._labeled_examples: list[tuple[CompoundObject, bool]] = []
        self._true_concept = true_concept

    def update(self, obj: CompoundObject, label: bool) -> None:
        """Update consistency scores after receiving a labeled example.

        Args:
            obj: The compound object that was labeled.
            label: True for positive example, False for negative.
        """
        self._labeled_examples.append((obj, label))
        for i, h in enumerate(self._hypothesis_space):
            h_says_positive = matches_hypothesis(obj, h)
            # Hypothesis is consistent with this example if its prediction matches
            if h_says_positive == label:
                self._consistency[i] += 1

    @property
    def _max_consistency(self) -> int:
        return max(self._consistency) if self._consistency else 0

    def _version_space_indices(self) -> list[int]:
        """Return indices of hypotheses in the current version space."""
        max_c = self._max_consistency
        return [i for i, c in enumerate(self._consistency) if c == max_c]

    @property
    def version_space(self) -> list[Hypothesis]:
        """Return the current version space (highest-consistency hypotheses)."""
        return [self._hypothesis_space[i] for i in self._version_space_indices()]

    @property
    def version_space_size(self) -> int:
        """Number of hypotheses in the version space."""
        return len(self._version_space_indices())

    @property
    def labeled_examples_count(self) -> int:
        """Number of labeled examples received so far."""
        return len(self._labeled_examples)

    def predict_label(self, obj: CompoundObject) -> tuple[Optional[bool], float]:
        """Predict label using query-by-committee vote.

        Returns:
            (predicted_label, confidence) where confidence in [0, 1].
            label is None when the vote is exactly 50/50.
        """
        vs = self.version_space
        if not vs:
            return None, 0.0

        votes_positive = sum(1 for h in vs if matches_hypothesis(obj, h))
        fraction_positive = votes_positive / len(vs)
        confidence = abs(fraction_positive - 0.5) * 2

        if confidence == 0.0:
            return None, 0.0
        predicted = fraction_positive > 0.5
        return predicted, confidence

    def is_informative(self, obj: CompoundObject) -> bool:
        """Return True if the object causes a non-trivial split in the version space."""
        vs = self.version_space
        if len(vs) <= 1:
            return False
        votes_positive = sum(1 for h in vs if matches_hypothesis(obj, h))
        return 0 < votes_positive < len(vs)

    def get_best_query(
        self, current_example: CompoundObject
    ) -> Optional[CompoundObject]:
        """Find the best query object using query-by-committee.

        The best query splits the version space as close to 50/50 as possible,
        constrained to objects differing from current_example by exactly one piece.
        Returns None if the version space has converged to 1 hypothesis.

        Args:
            current_example: The currently displayed compound object.

        Returns:
            The best query compound object, or None if already converged.
        """
        if self.version_space_size <= 1:
            return None

        vs = self.version_space
        n = len(vs)

        # First try: objects differing by exactly one piece
        candidates = [
            obj
            for obj in self._instance_space
            if obj != current_example and current_example.differs_by_one_piece(obj)
        ]

        best = _find_best_split(candidates, vs, n)
        if best is not None:
            return best

        # Fallback: allow any object
        all_candidates = [obj for obj in self._instance_space if obj != current_example]
        return _find_best_split(all_candidates, vs, n)

    @property
    def current_accuracy(self) -> Optional[float]:
        """F1-score against the true concept, or None if no true concept set."""
        if self._true_concept is None or self._true_concept not in CONCEPTS:
            return None
        true_h = CONCEPTS[self._true_concept]

        tp = fp = fn = 0
        for obj in self._instance_space:
            true_pos = matches_hypothesis(obj, true_h)
            pred, _ = self.predict_label(obj)
            pred_pos = pred is True
            if true_pos and pred_pos:
                tp += 1
            elif not true_pos and pred_pos:
                fp += 1
            elif true_pos and not pred_pos:
                fn += 1

        if tp + fp == 0 or tp + fn == 0:
            return 0.0
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        if precision + recall == 0:
            return 0.0
        return 2 * precision * recall / (precision + recall)


def _find_best_split(
    candidates: list[CompoundObject],
    vs: list[Hypothesis],
    n: int,
) -> Optional[CompoundObject]:
    """Find the candidate that best splits the version space."""
    best_obj: Optional[CompoundObject] = None
    best_score = float("inf")  # lower is better (closer to 0.5)

    for obj in candidates:
        votes_positive = sum(1 for h in vs if matches_hypothesis(obj, h))
        # Score = distance from perfect 50/50 split
        score = abs(votes_positive / n - 0.5)
        if score < best_score:
            best_score = score
            best_obj = obj

    return best_obj
