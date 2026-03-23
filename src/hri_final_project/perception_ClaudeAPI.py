"""Perception module using the Claude VLM API."""

import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

import anthropic
from dotenv import load_dotenv

from hri_final_project.compound_object import CompoundObject

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


_COMPOUND_OBJECT_PROMPT = (
    "You are a vision system for a robot experiment. In the image, there are"
    " exactly two paper cutout shapes placed in a demonstration area on a black"
    ' tablecloth. One shape is on top and one is on the bottom from the robot\'s'
    ' perspective (i.e., the shape closer to the back of the table is "top" and'
    ' the shape closer to the front of the table is "bottom").\n\n'
    "For each shape, identify:\n"
    "- color: must be exactly one of [pink, green, yellow, orange]\n"
    "- shape: must be exactly one of [circle, triangle, square]\n"
    "- size: must be exactly one of [small, large]\n\n"
    "Return your answer ONLY as a JSON object in this exact format, with no"
    " explanation or extra text:\n\n"
    '{\n  "top": {\n    "color": "",\n    "shape": "",\n    "size": ""\n  },\n'
    '  "bottom": {\n    "color": "",\n    "shape": "",\n    "size": ""\n  }\n}\n\n'
    "If you cannot confidently identify a property, still choose the closest"
    " match from the allowed values. Do not return null or unknown."
)

_perception_instance: ClaudePerception | None = None


def perceive_compound_object(image_path: Path) -> CompoundObject:
    """Run image perception and return a CompoundObject.

    Args:
        image_path: Path to the image file.

    Returns:
        CompoundObject parsed from the model's JSON response.
    """
    global _perception_instance  # noqa: PLW0603
    if _perception_instance is None:
        _perception_instance = ClaudePerception()

    result = _perception_instance.query(image_path, _COMPOUND_OBJECT_PROMPT)
    raw = result.answer.strip().strip("` \n").removeprefix("json").strip()
    data: dict[str, dict[str, str]] = json.loads(raw)
    top = data["top"]
    bottom = data["bottom"]
    return CompoundObject(
        color_top=top["color"],
        shape_top=top["shape"],
        size_top=top["size"],
        color_bottom=bottom["color"],
        shape_bottom=bottom["shape"],
        size_bottom=bottom["size"],
    )


# Backward-compatible alias.
MoonDreamPerception = ClaudePerception
