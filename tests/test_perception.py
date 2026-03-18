"""Tests for perception.py."""

from pathlib import Path

import pytest

from hri_final_project.perception import MoonDreamPerception

# Customize this prompt to ask the model whatever you want about each image.
PROMPT = "What is the shape, color, and size (big or small) of the two objects on the black paper?"

DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="session")
def perception() -> MoonDreamPerception:
    """Load MoonDream once for the entire test session."""
    return MoonDreamPerception()


def test_perception_on_img1(perception: MoonDreamPerception) -> None:
    """Run MoonDream on img1.png and print the model's answer."""
    image_path = DATA_DIR / "img1.png"
    result = perception.query(image_path, PROMPT)
    print(f"\n[{image_path.name}] {result.answer}")
