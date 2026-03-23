"""Domain representation for compound objects in the HRI experiment."""

from dataclasses import dataclass
from itertools import product
from typing import Any

COLORS: tuple[str, ...] = ("pink", "green", "yellow", "orange")
SHAPES: tuple[str, ...] = ("square", "triangle", "circle")
SIZES: tuple[str, ...] = ("small", "large")
WILDCARD = "*"

FEATURE_VALUES: dict[str, tuple[str, ...]] = {
    "color_top": COLORS,
    "shape_top": SHAPES,
    "size_top": SIZES,
    "color_bottom": COLORS,
    "shape_bottom": SHAPES,
    "size_bottom": SIZES,
}

FEATURE_ORDER: tuple[str, ...] = (
    "color_top",
    "shape_top",
    "size_top",
    "color_bottom",
    "shape_bottom",
    "size_bottom",
)


@dataclass(frozen=True)
class CompoundObject:
    """A compound object with a top and bottom piece."""

    color_top: str
    shape_top: str
    size_top: str
    color_bottom: str
    shape_bottom: str
    size_bottom: str

    def top_piece(self) -> tuple[str, str, str]:
        """Return the top piece as a tuple."""
        return (self.color_top, self.shape_top, self.size_top)

    def bottom_piece(self) -> tuple[str, str, str]:
        """Return the bottom piece as a tuple."""
        return (self.color_bottom, self.shape_bottom, self.size_bottom)

    def to_dict(self) -> dict[str, str]:
        """Convert to a plain dict."""
        return {
            "color_top": self.color_top,
            "shape_top": self.shape_top,
            "size_top": self.size_top,
            "color_bottom": self.color_bottom,
            "shape_bottom": self.shape_bottom,
            "size_bottom": self.size_bottom,
        }

    @staticmethod
    def from_dict(d: dict[str, str]) -> "CompoundObject":
        """Construct from a plain dict."""
        return CompoundObject(
            color_top=d["color_top"],
            shape_top=d["shape_top"],
            size_top=d["size_top"],
            color_bottom=d["color_bottom"],
            shape_bottom=d["shape_bottom"],
            size_bottom=d["size_bottom"],
        )

    def differs_by_one_piece(self, other: "CompoundObject") -> bool:
        """Return True if exactly one of (top, bottom) pieces differs."""
        top_same = self.top_piece() == other.top_piece()
        bottom_same = self.bottom_piece() == other.bottom_piece()
        return top_same != bottom_same  # exactly one differs


def generate_instance_space() -> list[CompoundObject]:
    """Generate all 552 valid compound objects (top piece != bottom piece)."""
    pieces = list(product(COLORS, SHAPES, SIZES))  # 24 unique pieces
    instances = []
    for top, bottom in product(pieces, pieces):
        if top != bottom:
            instances.append(
                CompoundObject(
                    color_top=top[0],
                    shape_top=top[1],
                    size_top=top[2],
                    color_bottom=bottom[0],
                    shape_bottom=bottom[1],
                    size_bottom=bottom[2],
                )
            )
    return instances


def matches_hypothesis(obj: CompoundObject, hypothesis: dict[str, str]) -> bool:
    """Return True if obj satisfies all constraints in the hypothesis.

    A hypothesis is a dict mapping feature names to required values.
    Missing features (or WILDCARD values) are unconstrained.
    """
    obj_dict = obj.to_dict()
    for feature, value in hypothesis.items():
        if value != WILDCARD and obj_dict.get(feature) != value:
            return False
    return True
