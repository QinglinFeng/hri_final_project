"""Runs the full experiment: 4 modes × 4 concepts per subject."""

from pathlib import Path
from typing import Optional

from hri_final_project.compound_object import CompoundObject
from hri_final_project.interaction_modes import ALMode, AQMode, InteractionMode, MIMode, SLMode
from hri_final_project.logger import ExperimentLogger
from hri_final_project.session_manager import SessionManager
from hri_final_project.version_space import VersionSpaceLearner

# Fixed assignment from Table IV of the paper
CONCEPT_MODE_ASSIGNMENT: list[tuple[str, str]] = [
    ("HOUSE", "SL"),
    ("SNOWMAN", "AL"),
    ("ALIEN", "MI"),
    ("ICE CREAM", "AQ"),
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

    def __init__(self, subject_id: str, log_dir: Path = Path("logs")) -> None:
        """Initialize the runner.

        Args:
            subject_id: Participant identifier.
            log_dir: Directory to write log files.
        """
        self._subject_id = subject_id
        log_path = log_dir / f"{subject_id}_experiment.jsonl"
        self._logger = ExperimentLogger(log_path)
        self._sessions: list[SessionManager] = []
        self._current_session_idx = 0

    def start_next_session(self) -> Optional[SessionManager]:
        """Create and return the next session, or None if experiment is done."""
        if self._current_session_idx >= len(CONCEPT_MODE_ASSIGNMENT):
            return None
        concept, mode_name = CONCEPT_MODE_ASSIGNMENT[self._current_session_idx]
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
        """Print a summary table after all sessions."""
        print("\n" + "=" * 60)
        print(f"EXPERIMENT SUMMARY — Subject: {self._subject_id}")
        print("=" * 60)
        print(f"{'Mode':<6} {'Concept':<12} {'Examples':>8} {'VS Size':>8}")
        print("-" * 60)
        for s in self._sessions:
            print(
                f"{s._mode_name:<6} {s._concept_name:<12} "  # noqa: SLF001
                f"{s._learner.labeled_examples_count:>8} "
                f"{s._learner.version_space_size:>8}"
            )
        print("=" * 60)
