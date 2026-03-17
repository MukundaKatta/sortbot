"""Waste composition analysis - tracking waste stream breakdown."""

from __future__ import annotations

from sortbot.classifier.categories import WasteCategory
from sortbot.models import WasteStream


class WasteCompositionAnalyzer:
    """Analyzes the composition of a waste stream by category.

    Tracks item counts, weights, and percentages per waste category
    to give an overview of how waste is distributed.
    """

    def __init__(self, stream: WasteStream) -> None:
        self.stream = stream

    def item_count_by_category(self) -> dict[WasteCategory, int]:
        """Return the number of items in each category."""
        return self.stream.category_breakdown()

    def weight_by_category(self) -> dict[WasteCategory, float]:
        """Return total weight (kg) in each category."""
        return self.stream.category_weight_breakdown()

    def percentage_by_category(self) -> dict[WasteCategory, float]:
        """Return percentage of items in each category (0-100)."""
        breakdown = self.stream.category_breakdown()
        total = self.stream.total_items
        if total == 0:
            return {cat: 0.0 for cat in WasteCategory}
        return {cat: (count / total) * 100.0 for cat, count in breakdown.items()}

    def weight_percentage_by_category(self) -> dict[WasteCategory, float]:
        """Return percentage of weight in each category (0-100)."""
        weights = self.stream.category_weight_breakdown()
        total = self.stream.total_weight_kg
        if total == 0.0:
            return {cat: 0.0 for cat in WasteCategory}
        return {cat: (w / total) * 100.0 for cat, w in weights.items()}

    def diversion_rate(self) -> float:
        """Calculate the waste diversion rate (percentage diverted from landfill).

        Items in recyclable, organic, compostable, and e-waste categories
        are considered diverted from general landfill.
        """
        divertable = {
            WasteCategory.RECYCLABLE,
            WasteCategory.ORGANIC,
            WasteCategory.COMPOSTABLE,
            WasteCategory.E_WASTE,
        }
        breakdown = self.stream.category_breakdown()
        total = self.stream.total_items
        if total == 0:
            return 0.0
        diverted = sum(count for cat, count in breakdown.items() if cat in divertable)
        return (diverted / total) * 100.0

    def contamination_flags(self) -> list[str]:
        """Identify potential contamination issues in the waste stream.

        Returns a list of warning messages.
        """
        flags: list[str] = []
        breakdown = self.stream.category_breakdown()
        total = self.stream.total_items

        if total == 0:
            return flags

        hazardous_count = breakdown.get(WasteCategory.HAZARDOUS, 0)
        if hazardous_count > 0:
            flags.append(
                f"{hazardous_count} hazardous item(s) detected. "
                "Ensure proper disposal at a certified facility."
            )

        ewaste_count = breakdown.get(WasteCategory.E_WASTE, 0)
        if ewaste_count > 0:
            flags.append(
                f"{ewaste_count} e-waste item(s) detected. "
                "Do not mix with general or recycling streams."
            )

        general_pct = (breakdown.get(WasteCategory.GENERAL, 0) / total) * 100
        if general_pct > 50:
            flags.append(
                f"General waste is {general_pct:.1f}% of the stream. "
                "Review sorting practices to improve diversion."
            )

        return flags
