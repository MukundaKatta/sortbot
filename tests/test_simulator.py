"""Tests for the synthetic data simulator."""

from sortbot.classifier.categories import WasteCategory
from sortbot.models import ClassifiedItem, WasteStream
from sortbot.simulator import generate_item, generate_stream


class TestGenerateItem:
    def test_returns_classified_item(self):
        item = generate_item(seed=42)
        assert isinstance(item, ClassifiedItem)

    def test_forced_category(self):
        item = generate_item(category=WasteCategory.E_WASTE, seed=42)
        assert item.result.category == WasteCategory.E_WASTE

    def test_confidence_in_valid_range(self):
        for i in range(20):
            item = generate_item(seed=i)
            assert 0.0 <= item.result.confidence <= 1.0

    def test_scores_sum_to_approximately_one(self):
        item = generate_item(seed=42)
        total = sum(item.result.scores.values())
        assert abs(total - 1.0) < 0.01

    def test_item_has_positive_weight(self):
        item = generate_item(seed=42)
        assert item.item.weight_kg > 0


class TestGenerateStream:
    def test_correct_item_count(self):
        stream = generate_stream(n_items=50, seed=42)
        assert isinstance(stream, WasteStream)
        assert stream.total_items == 50

    def test_stream_name(self):
        stream = generate_stream(stream_name="my_test", seed=42)
        assert stream.name == "my_test"

    def test_reproducible_with_seed(self):
        s1 = generate_stream(n_items=10, seed=123)
        s2 = generate_stream(n_items=10, seed=123)
        cats1 = [ci.result.category for ci in s1.items]
        cats2 = [ci.result.category for ci in s2.items]
        assert cats1 == cats2

    def test_custom_distribution(self):
        dist = {
            WasteCategory.RECYCLABLE: 1.0,
            WasteCategory.ORGANIC: 0.0,
            WasteCategory.E_WASTE: 0.0,
            WasteCategory.HAZARDOUS: 0.0,
            WasteCategory.GENERAL: 0.0,
            WasteCategory.COMPOSTABLE: 0.0,
        }
        stream = generate_stream(n_items=20, distribution=dist, seed=42)
        for ci in stream.items:
            assert ci.result.category == WasteCategory.RECYCLABLE
