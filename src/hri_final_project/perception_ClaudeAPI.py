"""Perception module using the Claude VLM API."""

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

import anthropic
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_MODEL = "claude-sonnet-4-6"


@dataclass(frozen=True)
class PerceptionResult:
    """Result of a VLM perception query."""

    image_path: Path
    prompt: str
    answer: str


class ClaudePerception:
    """Perception using the Claude API for image understanding."""

    def __init__(self, model: str = _DEFAULT_MODEL) -> None:
        """Initialize the Claude API client.

        Args:
            model: Claude model ID to use for vision queries.
        """
        self._client = anthropic.Anthropic()
        self._model = model

    def query(self, image_path: Path, prompt: str) -> PerceptionResult:
        """Query Claude with an image and a classification prompt.

        Args:
            image_path: Path to the image file.
            prompt: Classification instruction or question for the VLM.

        Returns:
            PerceptionResult containing the model's answer.
        """
        image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
        suffix = image_path.suffix.lower()
        media_type_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = cast(
            Literal["image/jpeg", "image/png", "image/gif", "image/webp"],
            media_type_map.get(suffix, "image/png"),
        )

        response = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        answer = next(
            (block.text for block in response.content if block.type == "text"), ""
        )
        return PerceptionResult(
            image_path=image_path,
            prompt=prompt,
            answer=answer,
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


# Backward-compatible alias.
MoonDreamPerception = ClaudePerception
