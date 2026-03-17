"""Pydantic data models for SORTBOT."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from sortbot.classifier.categories import WasteCategory


class WasteItem(BaseModel):
    """Represents a single waste item to be classified."""

    name: str = Field(..., description="Name or description of the waste item")
    source: str = Field(default="unknown", description="Where the item came from (e.g., kitchen, office)")
    weight_kg: float = Field(default=0.0, ge=0.0, description="Weight in kilograms")
    image_path: str | None = Field(default=None, description="Path to the item's image")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the item was recorded")


class ClassificationResult(BaseModel):
    """Result of classifying a waste item."""

    category: WasteCategory = Field(..., description="Predicted waste category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the prediction")
    scores: dict[str, float] = Field(
        default_factory=dict,
        description="Confidence scores for all categories",
    )
    processing_time_ms: float | None = Field(default=None, description="Inference time in milliseconds")

    @property
    def is_high_confidence(self) -> bool:
        """Return True if confidence exceeds 0.8."""
        return self.confidence >= 0.8

    @property
    def disposal_instructions(self) -> str:
        """Shortcut to disposal instructions for the predicted category."""
        return self.category.disposal_instructions


class WasteStream(BaseModel):
    """Aggregated collection of classified waste items over a period."""

    name: str = Field(default="default", description="Name of this waste stream")
    items: list[ClassifiedItem] = Field(default_factory=list, description="All classified items in this stream")

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def total_weight_kg(self) -> float:
        return sum(item.item.weight_kg for item in self.items)

    def category_breakdown(self) -> dict[WasteCategory, int]:
        """Count of items per category."""
        counts: dict[WasteCategory, int] = {}
        for ci in self.items:
            counts[ci.result.category] = counts.get(ci.result.category, 0) + 1
        return counts

    def category_weight_breakdown(self) -> dict[WasteCategory, float]:
        """Total weight per category."""
        weights: dict[WasteCategory, float] = {}
        for ci in self.items:
            cat = ci.result.category
            weights[cat] = weights.get(cat, 0.0) + ci.item.weight_kg
        return weights

    def average_confidence(self) -> float:
        """Mean classification confidence across all items."""
        if not self.items:
            return 0.0
        return sum(ci.result.confidence for ci in self.items) / len(self.items)


class ClassifiedItem(BaseModel):
    """A waste item paired with its classification result."""

    item: WasteItem
    result: ClassificationResult


# Rebuild WasteStream so the forward reference to ClassifiedItem resolves.
WasteStream.model_rebuild()
