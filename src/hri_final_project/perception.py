"""Perception module using a local MoonDream VLM."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image  # type: ignore[import-untyped]
from transformers import AutoModelForCausalLM  # type: ignore[import-untyped]

_DEFAULT_MODEL_ID = "vikhyatk/moondream2"
_DEFAULT_REVISION = "2025-06-21"
# To use MoonDream3 (gated, requires HuggingFace login):
#   model_id="moondream/moondream3-preview"


@dataclass(frozen=True)
class PerceptionResult:
    """Result of a VLM perception query."""

    image_path: Path
    prompt: str
    answer: str


class MoonDreamPerception:
    """Perception using a local MoonDream VLM for image understanding."""

    def __init__(
        self,
        model_id: str = _DEFAULT_MODEL_ID,
        revision: str = _DEFAULT_REVISION,
    ) -> None:
        """Load MoonDream model locally from HuggingFace.

        Args:
            model_id: HuggingFace model ID. Use "moondream/moondream3-preview"
                for MoonDream3 (requires `huggingface-cli login`).
            revision: Model revision/commit hash.
        """
        self._model: Any = AutoModelForCausalLM.from_pretrained(
            model_id,
            revision=revision,
            trust_remote_code=True,
        )

    def query(self, image_path: Path, prompt: str) -> PerceptionResult:
        """Query the VLM with an image and a classification prompt.

        Args:
            image_path: Path to the image file.
            prompt: Classification instruction or question for the VLM.

        Returns:
            PerceptionResult containing the model's answer.
        """
        image = Image.open(image_path)
        result: dict[str, str] = self._model.query(image=image, question=prompt)
        return PerceptionResult(
            image_path=image_path,
            prompt=prompt,
            answer=result["answer"],
        )

    def query_batch(
        self, image_paths: list[Path], prompt: str
    ) -> list[PerceptionResult]:
        """Query multiple images with the same prompt.

        Args:
            image_paths: List of paths to image files.
            prompt: Classification instruction or question for the VLM.

        Returns:
            List of PerceptionResult, one per image, in the same order.
        """
        return [self.query(path, prompt) for path in image_paths]
