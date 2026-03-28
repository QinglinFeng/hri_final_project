"""Runs the full experiment: 4 modes × 4 concepts per subject."""

import random
from itertools import permutations
from pathlib import Path
from typing import Optional

from hri_final_project.interaction_modes import ALMode, AQMode, InteractionMode, MIMode, SLMode
from hri_final_project.logger import ExperimentLogger
from hri_final_project.session_manager import SessionManager
from hri_final_project.version_space import VersionSpaceLearner

# SL is always first (HOUSE), per Table IV of the paper.
# The three interactive modes (AL, MI, AQ) are randomized across subjects.
_SL_SESSION: tuple[str, str] = ("HOUSE", "SL")

_INTERACTIVE_SESSIONS: list[tuple[str, str]] = [
    ("SNOWMAN", "AL"),
    ("ALIEN", "MI"),
    ("ICE CREAM", "AQ"),
]

# All 6 possible orderings of the 3 interactive sessions
ORDERINGS: list[list[tuple[str, str]]] = [
    list(p) for p in permutations(_INTERACTIVE_SESSIONS)
]


def _make_mode(mode_name: str, learner: VersionSpaceLearner) -> InteractionMode:
    """Instantiate an interaction mode by name."""
    modes: dict[str, InteractionMode] = {
        "SL": SLMode(learner),
        "AL": ALMode(learner),
        "MI": MIMode(learner),
        "AQ": AQMode(learner),
    }
    return modes[mode_name]


class ExperimentRunner:
    """Manages the full experiment session for one subject."""

    def __init__(
        self,
        subject_id: str,
        log_dir: Path = Path("logs"),
        order_seed: Optional[int] = None,
    ) -> None:
        """Initialize the runner.

        Args:
            subject_id: Participant identifier.
            log_dir: Directory to write log files.
            order_seed: Seed for randomizing the interactive mode order (0–5).
                        If None, picks randomly. Pass a fixed int for reproducibility.
        """
        self._subject_id = subject_id
        log_path = log_dir / f"{subject_id}_experiment.jsonl"
        self._logger = ExperimentLogger(log_path)
        self._sessions: list[SessionManager] = []
        self._current_session_idx = 0

        # Determine session order: SL always first, then randomized interactive
        if order_seed is None:
            ordering = random.choice(ORDERINGS)
        else:
            ordering = ORDERINGS[order_seed % len(ORDERINGS)]

        self._assignment: list[tuple[str, str]] = [_SL_SESSION] + ordering
        print(f"[Runner] Session order for {subject_id}:")
        for i, (concept, mode) in enumerate(self._assignment, 1):
            print(f"  {i}. {concept} [{mode}]")

    def start_next_session(self) -> Optional[SessionManager]:
        """Create and return the next session, or None if experiment is done."""
        if self._current_session_idx >= len(self._assignment):
            return None
        concept, mode_name = self._assignment[self._current_session_idx]
        self._current_session_idx += 1

        learner = VersionSpaceLearner(true_concept=concept)
        mode = _make_mode(mode_name, learner)
        session = SessionManager(
            subject_id=self._subject_id,
            concept_name=concept,
            mode_name=mode_name,
            mode=mode,
            learner=learner,
            logger=self._logger,
        )
        self._sessions.append(session)
        return session

    def print_summary(self) -> None:
        """Print a summary table after all sessions (matches Table V of the paper)."""
        print("\n" + "=" * 70)
        print(f"EXPERIMENT SUMMARY — Subject: {self._subject_id}")
        print("=" * 70)
        print(
            f"{'Mode':<6} {'Concept':<12} {'Examples':>9} "
            f"{'VS Size':>8} {'F1 Score':>10} {'Converged':>10}"
        )
        print("-" * 70)
        for s in self._sessions:
            f1 = s._learner.current_accuracy  # noqa: SLF001
            vs_size = s._learner.version_space_size  # noqa: SLF001
            converged = vs_size == 1
            f1_str = f"{f1:.3f}" if f1 is not None else "N/A"
            print(
                f"{s._mode_name:<6} {s._concept_name:<12} "  # noqa: SLF001
                f"{s._learner.labeled_examples_count:>9} "  # noqa: SLF001
                f"{vs_size:>8} "
                f"{f1_str:>10} "
                f"{'Yes' if converged else 'No':>10}"
            )
        print("=" * 70)
