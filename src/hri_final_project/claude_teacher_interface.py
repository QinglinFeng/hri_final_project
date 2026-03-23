"""Parse natural language teacher utterances via the Claude API."""

import json
import time
from typing import Optional

import anthropic
from dotenv import load_dotenv

from hri_final_project.compound_object import CompoundObject

load_dotenv()

_MODEL = "claude-sonnet-4-6"

_SYSTEM_TEMPLATE = """\
You are parsing teacher utterances in a robot teaching experiment.
The teacher is currently showing this compound object:
  Top piece: {color_top} {size_top} {shape_top}
  Bottom piece: {color_bottom} {size_bottom} {shape_bottom}
The concept being taught is: {concept_name}

Classify the teacher's utterance into exactly one of these types and return valid JSON only:
- positive_label: teacher says this IS an example of the concept
- negative_label: teacher says this is NOT an example
- test_question: teacher asks the robot to predict
- any_questions: teacher invites the robot to ask a question
- end_session: teacher says they are done

Return JSON: {{"type": "<type>"}}\
"""


class TeacherUtteranceParser:
    """Parses teacher utterances into structured commands using the Claude API."""

    def __init__(self) -> None:
        """Initialize the Anthropic client."""
        self._client = anthropic.Anthropic()

    def parse(
        self,
        utterance: str,
        current_object: CompoundObject,
        concept_name: str,
        max_retries: int = 3,
    ) -> dict[str, object]:
        """Parse a teacher utterance into a structured command.

        Args:
            utterance: The raw teacher utterance string.
            current_object: The compound object currently on display.
            concept_name: The name of the concept being taught.
            max_retries: Number of retries on API failure.

        Returns:
            A dict with at least a "type" key.
        """
        system = _SYSTEM_TEMPLATE.format(
            color_top=current_object.color_top,
            size_top=current_object.size_top,
            shape_top=current_object.shape_top,
            color_bottom=current_object.color_bottom,
            size_bottom=current_object.size_bottom,
            shape_bottom=current_object.shape_bottom,
            concept_name=concept_name,
        )

        last_error: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                response = self._client.messages.create(
                    model=_MODEL,
                    max_tokens=256,
                    system=system,
                    messages=[{"role": "user", "content": utterance}],
                )
                text = next(
                    (b.text for b in response.content if b.type == "text"), ""
                ).strip()
                parsed: dict[str, object] = json.loads(text)
                if "type" not in parsed:
                    raise ValueError(f"Missing 'type' in response: {text}")
                return parsed
            except (anthropic.APIError, json.JSONDecodeError, ValueError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)

        raise RuntimeError(
            f"Failed to parse utterance after {max_retries} attempts"
        ) from last_error
