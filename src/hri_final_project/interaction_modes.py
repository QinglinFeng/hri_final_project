"""Interaction mode implementations from Cakmak et al.

(2010).
"""

from abc import ABC, abstractmethod
from typing import Optional

from hri_final_project.compound_object import CompoundObject, generate_instance_space
from hri_final_project.version_space import VersionSpaceLearner


class InteractionMode(ABC):
    """Abstract base class for interaction modes."""

    def __init__(self, learner: VersionSpaceLearner) -> None:
        """Initialize with a shared version space learner.

        Args:
            learner: The version space learner instance.
        """
        self._learner = learner

    @abstractmethod
    def on_label_received(
        self, label: bool, compound_obj: CompoundObject
    ) -> Optional[CompoundObject]:
        """Called when a label is received for a compound object.

        Args:
            label: True for positive, False for negative.
            compound_obj: The labeled compound object.

        Returns:
            A query object if the mode wants to ask a question, else None.
        """


class SLMode(InteractionMode):
    """Supervised Learning: passive baseline, never queries."""

    def on_label_received(
        self, label: bool, compound_obj: CompoundObject
    ) -> Optional[CompoundObject]:
        """Accept label passively; never issue a query."""
        return None


class ALMode(InteractionMode):
    """Active Learning: queries after every label."""

    def on_label_received(
        self, label: bool, compound_obj: CompoundObject
    ) -> Optional[CompoundObject]:
        """Issue best query after every label."""
        return self._learner.get_best_query(compound_obj)


class MIMode(InteractionMode):
    """Mixed Initiative: queries when uninformative or the instance space is mostly uninformative."""  # pylint: disable=line-too-long

    _UNINFORMATIVE_THRESHOLD = 0.8

    def on_label_received(
        self, label: bool, compound_obj: CompoundObject
    ) -> Optional[CompoundObject]:
        """Query if the received example was uninformative, or >80% of space is
        uninformative."""
        # Check if this example was uninformative (post-update check)
        example_uninformative = not self._learner.is_informative(compound_obj)

        if example_uninformative:
            return self._learner.get_best_query(compound_obj)

        # Check if >80% of instance space is uninformative
        instance_space = generate_instance_space()
        uninformative_count = sum(
            1 for obj in instance_space if not self._learner.is_informative(obj)
        )
        fraction_uninformative = uninformative_count / len(instance_space)
        if fraction_uninformative > self._UNINFORMATIVE_THRESHOLD:
            return self._learner.get_best_query(compound_obj)

        return None


class AQMode(InteractionMode):
    """Any Questions: only queries when teacher explicitly invites questions."""

    def on_label_received(
        self, label: bool, compound_obj: CompoundObject
    ) -> Optional[CompoundObject]:
        """Labels are accepted passively; queries only triggered by on_any_questions."""
        return None

    def on_any_questions(self, current_obj: CompoundObject) -> Optional[CompoundObject]:
        """Trigger a query when the teacher says 'do you have any questions?'.

        Args:
            current_obj: The currently displayed compound object.

        Returns:
            Best query object, or None if converged.
        """
        return self._learner.get_best_query(current_obj)
