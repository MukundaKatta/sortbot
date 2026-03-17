"""Recycling advisor - provides disposal guidance per item."""

from __future__ import annotations

from dataclasses import dataclass

from sortbot.classifier.categories import WasteCategory
from sortbot.models import ClassificationResult, WasteItem


@dataclass
class DisposalAdvice:
    """Structured disposal guidance for a waste item."""

    item_name: str
    category: WasteCategory
    bin_color: str
    instructions: str
    confidence_note: str
    alternatives: list[str]


class RecyclingAdvisor:
    """Provides actionable disposal guidance based on classification results."""

    CONFIDENCE_THRESHOLD_HIGH = 0.8
    CONFIDENCE_THRESHOLD_LOW = 0.4

    def advise(self, item: WasteItem, result: ClassificationResult) -> DisposalAdvice:
        """Generate disposal advice for a classified waste item.

        Args:
            item: The waste item that was classified.
            result: The classification result.

        Returns:
            DisposalAdvice with bin color, instructions, and confidence notes.
        """
        category = result.category

        if result.confidence >= self.CONFIDENCE_THRESHOLD_HIGH:
            confidence_note = "High confidence classification. Follow the instructions below."
        elif result.confidence >= self.CONFIDENCE_THRESHOLD_LOW:
            confidence_note = (
                "Moderate confidence. If unsure, inspect the item's material "
                "or check local recycling guidelines."
            )
        else:
            confidence_note = (
                "Low confidence classification. Please verify the item manually "
                "or consult your local waste management authority."
            )

        alternatives = self._suggest_alternatives(item, category)

        return DisposalAdvice(
            item_name=item.name,
            category=category,
            bin_color=category.bin_color,
            instructions=category.disposal_instructions,
            confidence_note=confidence_note,
            alternatives=alternatives,
        )

    def _suggest_alternatives(self, item: WasteItem, category: WasteCategory) -> list[str]:
        """Suggest waste-reduction alternatives when applicable."""
        suggestions: list[str] = []

        if category == WasteCategory.GENERAL:
            suggestions.append("Consider whether this item could be repaired or repurposed.")
            suggestions.append("Check if a local donation center accepts similar items.")

        if category == WasteCategory.RECYCLABLE:
            suggestions.append("Opt for reusable alternatives to reduce recycling volume.")

        if category in (WasteCategory.ORGANIC, WasteCategory.COMPOSTABLE):
            suggestions.append("Home composting can turn this waste into nutrient-rich soil.")

        if category == WasteCategory.E_WASTE:
            suggestions.append("Many electronics retailers offer trade-in or take-back programs.")
            suggestions.append("Consider donating working electronics to schools or nonprofits.")

        if category == WasteCategory.HAZARDOUS:
            suggestions.append("Look for manufacturer take-back programs for this product.")
            suggestions.append("Switch to less hazardous alternatives where possible.")

        return suggestions

    def batch_advise(
        self,
        items_and_results: list[tuple[WasteItem, ClassificationResult]],
    ) -> list[DisposalAdvice]:
        """Generate advice for multiple items at once."""
        return [self.advise(item, result) for item, result in items_and_results]
