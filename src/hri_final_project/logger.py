"""JSON Lines event logger for the HRI experiment."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from hri_final_project.compound_object import CompoundObject


class ExperimentLogger:
    """Logs experiment events to a JSON Lines file."""

    def __init__(self, log_path: Path) -> None:
        """Initialize the logger.

        Args:
            log_path: Path to the output .jsonl file.
        """
        self._log_path = log_path
        log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        subject_id: str,
        mode: str,
        concept: str,
        interaction_step: int,
        current_example: CompoundObject,
        sentence_type: str,
        current_label: Optional[bool],
        answer_type: Optional[str],
        query: Optional[CompoundObject],
        version_space_size: int,
        is_informative: Optional[bool],
    ) -> None:
        """Append one event record to the log file."""
        record = {
            "subject_id": subject_id,
            "mode": mode,
            "concept": concept,
            "system_time": datetime.now().isoformat(),
            "interaction_step": interaction_step,
            "current_example": current_example.to_dict(),
            "sentence_type": sentence_type,
            "current_label": current_label,
            "answer_type": answer_type,
            "query": query.to_dict() if query is not None else None,
            "version_space_size": version_space_size,
            "is_informative": is_informative,
        }
        with self._log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
