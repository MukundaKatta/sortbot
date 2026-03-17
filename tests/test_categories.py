"""Tests for waste category definitions."""

from sortbot.classifier.categories import WasteCategory


class TestWasteCategory:
    def test_all_six_categories_exist(self):
        assert WasteCategory.count() == 6

    def test_category_values(self):
        expected = {"recyclable", "organic", "e-waste", "hazardous", "general", "compostable"}
        actual = {c.value for c in WasteCategory}
        assert actual == expected

    def test_label_index_roundtrip(self):
        for cat in WasteCategory:
            idx = cat.label_index
            assert WasteCategory.from_index(idx) == cat

    def test_from_index_invalid_raises(self):
        import pytest
        with pytest.raises(ValueError):
            WasteCategory.from_index(99)

    def test_disposal_instructions_not_empty(self):
        for cat in WasteCategory:
            assert len(cat.disposal_instructions) > 10

    def test_bin_color_not_empty(self):
        for cat in WasteCategory:
            assert cat.bin_color

    def test_examples_not_empty(self):
        for cat in WasteCategory:
            assert len(cat.examples) >= 3
