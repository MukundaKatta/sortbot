"""Waste category definitions with disposal instructions."""

from enum import Enum


class WasteCategory(str, Enum):
    """Six-category waste classification system."""

    RECYCLABLE = "recyclable"
    ORGANIC = "organic"
    E_WASTE = "e-waste"
    HAZARDOUS = "hazardous"
    GENERAL = "general"
    COMPOSTABLE = "compostable"

    @property
    def label_index(self) -> int:
        """Return the integer label index for this category."""
        return list(WasteCategory).index(self)

    @property
    def disposal_instructions(self) -> str:
        """Return disposal guidance for this waste category."""
        return _DISPOSAL_INSTRUCTIONS[self]

    @property
    def bin_color(self) -> str:
        """Return the conventional bin color for this category."""
        return _BIN_COLORS[self]

    @property
    def examples(self) -> list[str]:
        """Return example items for this category."""
        return _EXAMPLES[self]

    @classmethod
    def from_index(cls, index: int) -> "WasteCategory":
        """Get category from its integer label index."""
        members = list(cls)
        if 0 <= index < len(members):
            return members[index]
        raise ValueError(f"Invalid category index: {index}. Must be 0-{len(members) - 1}.")

    @classmethod
    def count(cls) -> int:
        """Return the number of categories."""
        return len(cls)


_DISPOSAL_INSTRUCTIONS: dict[WasteCategory, str] = {
    WasteCategory.RECYCLABLE: (
        "Clean and dry the item. Remove caps and labels where possible. "
        "Place in the recycling bin. Do not bag recyclables in plastic bags."
    ),
    WasteCategory.ORGANIC: (
        "Place in the organic waste bin. Avoid mixing with non-organic materials. "
        "Food-soiled paper can go here. No plastics, even if labeled biodegradable."
    ),
    WasteCategory.E_WASTE: (
        "Do NOT place in regular bins. Take to a certified e-waste collection point "
        "or schedule a pickup. Remove batteries if possible and recycle separately."
    ),
    WasteCategory.HAZARDOUS: (
        "Do NOT place in any regular bin. Store safely and take to a hazardous waste "
        "drop-off facility. Keep in original containers. Never pour down drains."
    ),
    WasteCategory.GENERAL: (
        "Place in the general waste bin. Consider whether the item can be reused "
        "or repurposed before disposal. Bag securely to prevent litter."
    ),
    WasteCategory.COMPOSTABLE: (
        "Place in the compost bin or home compost pile. Break into smaller pieces "
        "for faster decomposition. Keep moist but not waterlogged."
    ),
}

_BIN_COLORS: dict[WasteCategory, str] = {
    WasteCategory.RECYCLABLE: "blue",
    WasteCategory.ORGANIC: "green",
    WasteCategory.E_WASTE: "orange",
    WasteCategory.HAZARDOUS: "red",
    WasteCategory.GENERAL: "black",
    WasteCategory.COMPOSTABLE: "brown",
}

_EXAMPLES: dict[WasteCategory, list[str]] = {
    WasteCategory.RECYCLABLE: [
        "plastic bottle", "aluminum can", "glass jar", "cardboard box",
        "newspaper", "steel tin", "paper bag",
    ],
    WasteCategory.ORGANIC: [
        "banana peel", "coffee grounds", "eggshell", "vegetable scraps",
        "grass clippings", "flower trimmings", "bread",
    ],
    WasteCategory.E_WASTE: [
        "smartphone", "laptop", "USB cable", "old TV", "circuit board",
        "printer cartridge", "headphones",
    ],
    WasteCategory.HAZARDOUS: [
        "paint can", "motor oil", "pesticide bottle", "fluorescent bulb",
        "medical syringe", "bleach container", "lithium battery",
    ],
    WasteCategory.GENERAL: [
        "chip bag", "styrofoam cup", "broken ceramic", "used tissue",
        "disposable diaper", "cigarette butt", "chewing gum",
    ],
    WasteCategory.COMPOSTABLE: [
        "leaves", "wood chips", "paper towel", "tea bag", "sawdust",
        "cotton fabric", "fruit core",
    ],
}
