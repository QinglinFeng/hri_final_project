"""Tests for perception.py."""

from pathlib import Path

import pytest

from hri_final_project.perception import MoonDreamPerception

# Customize this prompt to ask the model whatever you want about each image.
PROMPT = "Describe what you see in this image."

DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.mark.parametrize(
    "image_path", sorted(DATA_DIR.glob("img*.png")), ids=lambda p: p.name
)
def test_perception_on_data_images(image_path: Path) -> None:
    """Run MoonDream on each data image and print the model's answer."""
    perception = MoonDreamPerception()
    result = perception.query(image_path, PROMPT)
    print(f"\n[{image_path.name}] {result.answer}")
