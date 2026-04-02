"""Session manager: orchestrates a full teaching session for one concept and mode."""

from typing import Optional

from hri_final_project.claude_teacher_interface import TeacherUtteranceParser
from hri_final_project.compound_object import CompoundObject
from hri_final_project.interaction_modes import AQMode, InteractionMode
from hri_final_project.logger import ExperimentLogger
from hri_final_project.version_space import VersionSpaceLearner


def _format_piece(color: str, size: str, shape: str) -> str:
    return f"{size} {color} {shape}"


def _query_to_text(current: CompoundObject, query: CompoundObject) -> str:
    """Phrase a query as a natural language replacement request."""
    if current.top_piece() != query.top_piece():
        piece = "top"
        c, sh, si = query.color_top, query.shape_top, query.size_top
    else:
        piece = "bottom"
        c, sh, si = query.color_bottom, query.shape_bottom, query.size_bottom
    return f"Can you replace the {piece} piece with a {si} {c} {sh}?"


class SessionManager:
    """Manages one teaching session for a single concept in a single interaction
    mode."""

    def __init__(
        self,
        subject_id: str,
        concept_name: str,
        mode_name: str,
        mode: InteractionMode,
        learner: VersionSpaceLearner,
        logger: ExperimentLogger,
    ) -> None:
        """Initialize the session manager.

        Args:
            subject_id: Participant identifier.
            concept_name: Name of the concept being taught.
            mode_name: Short name of the interaction mode (SL/AL/MI/AQ).
            mode: The interaction mode instance.
            learner: The version space learner.
            logger: The event logger.
        """
        self._subject_id = subject_id
        self._concept_name = concept_name
        self._mode_name = mode_name
        self._mode = mode
        self._learner = learner
        self._logger = logger
        self._parser = TeacherUtteranceParser()
        self._step = 0
        self._active = True
        self.robot_response: str = ""

    @property
    def is_active(self) -> bool:
        """True while the session is ongoing."""
        return self._active

    def process_turn(self, utterance: str, current_object: CompoundObject) -> None:
        """Process one teacher turn.

        Args:
            utterance: The teacher's spoken utterance.
            current_object: The compound object currently on display.
        """
        self._step += 1
        parsed = self._parser.parse(utterance, current_object, self._concept_name)
        sentence_type: str = str(parsed.get("type", "unknown"))

        label: Optional[bool] = None
        answer_type: Optional[str] = None
        query: Optional[CompoundObject] = None
        informative: Optional[bool] = None

        if sentence_type in ("positive_label", "negative_label"):
            label = sentence_type == "positive_label"
            informative = self._learner.is_informative(current_object)
            self._learner.update(current_object, label)
            query = self._mode.on_label_received(label, current_object)

            if query is not None:
                answer_type = "query"
                self.robot_response = (
                    f"Understood! {_query_to_text(current_object, query)}"
                )
            else:
                answer_type = "acknowledgement"
                self.robot_response = "Understood, thank you!"

        elif sentence_type == "test_question":
            predicted, confidence = self._learner.predict_label(current_object)
            answer_type = "answer"
            if predicted is None:
                self.robot_response = "I'm not sure — I think it could go either way."
            elif predicted:
                self.robot_response = (
                    f"Yes, I think this IS a {self._concept_name} "
                    f"(confidence: {confidence:.0%})."
                )
            else:
                self.robot_response = (
                    f"No, I don't think this is a {self._concept_name} "
                    f"(confidence: {confidence:.0%})."
                )

        elif sentence_type == "any_questions":
            answer_type = "query"
            if isinstance(self._mode, AQMode):
                query = self._mode.on_any_questions(current_object)
            if query is not None:
                self.robot_response = _query_to_text(current_object, query)
            else:
                answer_type = "turn_pass"
                self.robot_response = "No, I'm good for now, thank you!"

        elif sentence_type == "end_session":
            answer_type = "acknowledgement"
            self.robot_response = "Thank you for teaching me!"
            self._active = False

        else:
            answer_type = "turn_pass"
            self.robot_response = "Sorry, I didn't understand that."

        self._logger.log(
            subject_id=self._subject_id,
            mode=self._mode_name,
            concept=self._concept_name,
            interaction_step=self._step,
            current_example=current_object,
            sentence_type=sentence_type,
            current_label=label,
            answer_type=answer_type,
            query=query,
            version_space_size=self._learner.version_space_size,
            is_informative=informative,
        )

    def status_line(self) -> str:
        """Return a brief status string for display."""
        return (
            f"[{self._mode_name}] concept={self._concept_name} "
            f"vs_size={self._learner.version_space_size} "
            f"examples={self._learner.labeled_examples_count}"
        )
