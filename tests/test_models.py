"""Tests for pydantic data models."""

import pytest

from sortbot.classifier.categories import WasteCategory
from sortbot.models import ClassificationResult, ClassifiedItem, WasteItem, WasteStream


class TestWasteItem:
    def test_create_minimal(self):
        item = WasteItem(name="plastic bottle")
        assert item.name == "plastic bottle"
        assert item.weight_kg == 0.0
        assert item.source == "unknown"

    def test_create_full(self):
        item = WasteItem(name="banana peel", source="kitchen", weight_kg=0.15)
        assert item.weight_kg == 0.15
        assert item.source == "kitchen"

    def test_negative_weight_rejected(self):
        with pytest.raises(Exception):
            WasteItem(name="test", weight_kg=-1.0)


class TestClassificationResult:
    def test_high_confidence(self):
        result = ClassificationResult(
            category=WasteCategory.RECYCLABLE,
            confidence=0.95,
        )
        assert result.is_high_confidence is True

    def test_low_confidence(self):
        result = ClassificationResult(
            category=WasteCategory.GENERAL,
            confidence=0.5,
        )
        assert result.is_high_confidence is False

    def test_disposal_instructions_accessible(self):
        result = ClassificationResult(
            category=WasteCategory.HAZARDOUS,
            confidence=0.9,
        )
        assert "hazardous" in result.disposal_instructions.lower()


class TestWasteStream:
    def _make_stream(self, categories: list[WasteCategory]) -> WasteStream:
        items = []
        for cat in categories:
            ci = ClassifiedItem(
                item=WasteItem(name="test", weight_kg=1.0),
                result=ClassificationResult(category=cat, confidence=0.9),
            )
            items.append(ci)
        return WasteStream(name="test_stream", items=items)

    def test_total_items(self):
        stream = self._make_stream([WasteCategory.RECYCLABLE, WasteCategory.ORGANIC])
        assert stream.total_items == 2

    def test_total_weight(self):
        stream = self._make_stream([WasteCategory.RECYCLABLE, WasteCategory.ORGANIC])
        assert stream.total_weight_kg == 2.0

    def test_category_breakdown(self):
        stream = self._make_stream([
            WasteCategory.RECYCLABLE,
            WasteCategory.RECYCLABLE,
            WasteCategory.ORGANIC,
        ])
        breakdown = stream.category_breakdown()
        assert breakdown[WasteCategory.RECYCLABLE] == 2
        assert breakdown[WasteCategory.ORGANIC] == 1

    def test_average_confidence(self):
        stream = self._make_stream([WasteCategory.GENERAL])
        assert stream.average_confidence() == 0.9

    def test_empty_stream(self):
        stream = WasteStream(name="empty")
        assert stream.total_items == 0
        assert stream.average_confidence() == 0.0
