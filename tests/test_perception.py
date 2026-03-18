"""Tests for perception.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
from PIL import Image  # type: ignore[import-untyped]

from hri_final_project.perception import MoonDreamPerception, PerceptionResult


def _make_image(path: Path, color: tuple[int, int, int], size: int = 64) -> None:
    """Save a solid-color PNG image."""
    arr = np.full((size, size, 3), color, dtype=np.uint8)
    Image.fromarray(arr).save(path)


def test_moondream_perception_query(tmp_path: Path) -> None:
    """MoonDreamPerception.query returns a PerceptionResult with the VLM answer."""
    image_path = tmp_path / "red_square.png"
    _make_image(image_path, color=(255, 0, 0))

    with patch("hri_final_project.perception.AutoModelForCausalLM") as mock_cls:
        mock_model = MagicMock()
        mock_cls.from_pretrained.return_value = mock_model
        mock_model.query.return_value = {"answer": "red square"}

        perception = MoonDreamPerception()
        result = perception.query(image_path, "What color is the shape?")

    assert isinstance(result, PerceptionResult)
    assert result.answer == "red square"
    assert result.image_path == image_path
    assert result.prompt == "What color is the shape?"
    mock_model.query.assert_called_once()


def test_moondream_perception_query_batch(tmp_path: Path) -> None:
    """MoonDreamPerception.query_batch returns one result per image."""
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    answers = ["red", "green", "blue"]
    paths = []
    for i, color in enumerate(colors):
        p = tmp_path / f"img_{i}.png"
        _make_image(p, color)
        paths.append(p)

    with patch("hri_final_project.perception.AutoModelForCausalLM") as mock_cls:
        mock_model = MagicMock()
        mock_cls.from_pretrained.return_value = mock_model
        mock_model.query.side_effect = [{"answer": a} for a in answers]

        perception = MoonDreamPerception()
        results = perception.query_batch(paths, "What color is this image?")

    assert len(results) == 3
    for result, expected_answer, expected_path in zip(results, answers, paths):
        assert result.answer == expected_answer
        assert result.image_path == expected_path
