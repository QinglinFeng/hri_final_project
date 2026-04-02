"""Tests for perception.py."""

# pylint: disable=redefined-outer-name
import json
from pathlib import Path

import pytest

from hri_final_project.perception_ClaudeAPI import MoonDreamPerception

# Customize this prompt to ask the model whatever you want about each image.
PROMPT = (
    "You are a vision system for a robot experiment. In the image, there are"
    " exactly two paper cutout shapes placed in a demonstration area on a black"
    " tablecloth. One shape is on top and one is on the bottom from the robot's"
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

DATA_DIR = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="session")
def perception() -> MoonDreamPerception:
    """Load MoonDream once for the entire test session."""
    return MoonDreamPerception()


def test_perception_on_img1(perception: MoonDreamPerception) -> None:
    """Run MoonDream on img1.png and print the model's answer."""
    image_path = DATA_DIR / "img1.png"
    result = perception.query(image_path, PROMPT)
    data = json.loads(result.answer.strip("` \n").removeprefix("json").strip())
    top = data["top"]
    bottom = data["bottom"]
    print(
        f"\n[{image_path.name}]"
        f"  top: {top['color']}, {top['shape']}, {top['size']}"
        f"  |  bottom: {bottom['color']}, {bottom['shape']}, {bottom['size']}"
    )


def test_perception_on_img2(perception: MoonDreamPerception) -> None:
    """Run MoonDream on img2.png and print the model's answer."""
    image_path = DATA_DIR / "img2.png"
    result = perception.query(image_path, PROMPT)
    data = json.loads(result.answer.strip("` \n").removeprefix("json").strip())
    top = data["top"]
    bottom = data["bottom"]
    print(
        f"\n[{image_path.name}]"
        f"  top: {top['color']}, {top['shape']}, {top['size']}"
        f"  |  bottom: {bottom['color']}, {bottom['shape']}, {bottom['size']}"
    )


def test_perception_on_img3(perception: MoonDreamPerception) -> None:
    """Run MoonDream on img3.png and print the model's answer."""
    image_path = DATA_DIR / "img3.png"
    result = perception.query(image_path, PROMPT)
    data = json.loads(result.answer.strip("` \n").removeprefix("json").strip())
    top = data["top"]
    bottom = data["bottom"]
    print(
        f"\n[{image_path.name}]"
        f"  top: {top['color']}, {top['shape']}, {top['size']}"
        f"  |  bottom: {bottom['color']}, {bottom['shape']}, {bottom['size']}"
    )


def test_perception_on_img4(perception: MoonDreamPerception) -> None:
    """Run MoonDream on img4.png and print the model's answer."""
    image_path = DATA_DIR / "img4.png"
    result = perception.query(image_path, PROMPT)
    data = json.loads(result.answer.strip("` \n").removeprefix("json").strip())
    top = data["top"]
    bottom = data["bottom"]
    print(
        f"\n[{image_path.name}]"
        f"  top: {top['color']}, {top['shape']}, {top['size']}"
        f"  |  bottom: {bottom['color']}, {bottom['shape']}, {bottom['size']}"
    )


def test_perception_on_img5(perception: MoonDreamPerception) -> None:
    """Run MoonDream on img5.png and print the model's answer."""
    image_path = DATA_DIR / "img5.png"
    result = perception.query(image_path, PROMPT)
    data = json.loads(result.answer.strip("` \n").removeprefix("json").strip())
    top = data["top"]
    bottom = data["bottom"]
    print(
        f"\n[{image_path.name}]"
        f"  top: {top['color']}, {top['shape']}, {top['size']}"
        f"  |  bottom: {bottom['color']}, {bottom['shape']}, {bottom['size']}"
    )


def test_perception_on_img6(perception: MoonDreamPerception) -> None:
    """Run MoonDream on img6.png and print the model's answer."""
    image_path = DATA_DIR / "img6.png"
    result = perception.query(image_path, PROMPT)
    data = json.loads(result.answer.strip("` \n").removeprefix("json").strip())
    top = data["top"]
    bottom = data["bottom"]
    print(
        f"\n[{image_path.name}]"
        f"  top: {top['color']}, {top['shape']}, {top['size']}"
        f"  |  bottom: {bottom['color']}, {bottom['shape']}, {bottom['size']}"
    )


def test_perception_on_img7(perception: MoonDreamPerception) -> None:
    """Run MoonDream on img7.png and print the model's answer."""
    image_path = DATA_DIR / "img7.png"
    result = perception.query(image_path, PROMPT)
    data = json.loads(result.answer.strip("` \n").removeprefix("json").strip())
    top = data["top"]
    bottom = data["bottom"]
    print(
        f"\n[{image_path.name}]"
        f"  top: {top['color']}, {top['shape']}, {top['size']}"
        f"  |  bottom: {bottom['color']}, {bottom['shape']}, {bottom['size']}"
    )


def test_perception_on_img8(perception: MoonDreamPerception) -> None:
    """Run MoonDream on img8.png and print the model's answer."""
    image_path = DATA_DIR / "img8.png"
    result = perception.query(image_path, PROMPT)
    data = json.loads(result.answer.strip("` \n").removeprefix("json").strip())
    top = data["top"]
    bottom = data["bottom"]
    print(
        f"\n[{image_path.name}]"
        f"  top: {top['color']}, {top['shape']}, {top['size']}"
        f"  |  bottom: {bottom['color']}, {bottom['shape']}, {bottom['size']}"
    )


def test_perception_on_img9(perception: MoonDreamPerception) -> None:
    """Run MoonDream on img9.png and print the model's answer."""
    image_path = DATA_DIR / "img9.png"
    result = perception.query(image_path, PROMPT)
    data = json.loads(result.answer.strip("` \n").removeprefix("json").strip())
    top = data["top"]
    bottom = data["bottom"]
    print(
        f"\n[{image_path.name}]"
        f"  top: {top['color']}, {top['shape']}, {top['size']}"
        f"  |  bottom: {bottom['color']}, {bottom['shape']}, {bottom['size']}"
    )


def test_perception_on_img10(perception: MoonDreamPerception) -> None:
    """Run MoonDream on img10.png and print the model's answer."""
    image_path = DATA_DIR / "img10.png"
    result = perception.query(image_path, PROMPT)
    data = json.loads(result.answer.strip("` \n").removeprefix("json").strip())
    top = data["top"]
    bottom = data["bottom"]
    print(
        f"\n[{image_path.name}]"
        f"  top: {top['color']}, {top['shape']}, {top['size']}"
        f"  |  bottom: {bottom['color']}, {bottom['shape']}, {bottom['size']}"
    )
