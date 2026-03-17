"""Tests for analyzer modules."""

from sortbot.analyzer.advisor import RecyclingAdvisor
from sortbot.analyzer.composition import WasteCompositionAnalyzer
from sortbot.analyzer.impact import EnvironmentalImpact
from sortbot.classifier.categories import WasteCategory
from sortbot.models import ClassificationResult, ClassifiedItem, WasteItem, WasteStream


def _make_classified_item(
    category: WasteCategory,
    weight: float = 1.0,
    confidence: float = 0.9,
) -> ClassifiedItem:
    return ClassifiedItem(
        item=WasteItem(name="test item", weight_kg=weight),
        result=ClassificationResult(category=category, confidence=confidence),
    )


def _make_stream(items: list[ClassifiedItem]) -> WasteStream:
    return WasteStream(name="test", items=items)


class TestWasteCompositionAnalyzer:
    def test_percentage_by_category(self):
        stream = _make_stream([
            _make_classified_item(WasteCategory.RECYCLABLE),
            _make_classified_item(WasteCategory.RECYCLABLE),
            _make_classified_item(WasteCategory.ORGANIC),
            _make_classified_item(WasteCategory.GENERAL),
        ])
        analyzer = WasteCompositionAnalyzer(stream)
        pcts = analyzer.percentage_by_category()
        assert pcts[WasteCategory.RECYCLABLE] == 50.0
        assert pcts[WasteCategory.ORGANIC] == 25.0

    def test_diversion_rate(self):
        stream = _make_stream([
            _make_classified_item(WasteCategory.RECYCLABLE),
            _make_classified_item(WasteCategory.ORGANIC),
            _make_classified_item(WasteCategory.GENERAL),
            _make_classified_item(WasteCategory.GENERAL),
        ])
        analyzer = WasteCompositionAnalyzer(stream)
        rate = analyzer.diversion_rate()
        assert rate == 50.0

    def test_contamination_flags_hazardous(self):
        stream = _make_stream([
            _make_classified_item(WasteCategory.HAZARDOUS),
            _make_classified_item(WasteCategory.RECYCLABLE),
        ])
        analyzer = WasteCompositionAnalyzer(stream)
        flags = analyzer.contamination_flags()
        assert any("hazardous" in f.lower() for f in flags)

    def test_empty_stream(self):
        stream = _make_stream([])
        analyzer = WasteCompositionAnalyzer(stream)
        assert analyzer.diversion_rate() == 0.0
        assert analyzer.contamination_flags() == []


class TestRecyclingAdvisor:
    def test_advise_high_confidence(self):
        advisor = RecyclingAdvisor()
        item = WasteItem(name="plastic bottle")
        result = ClassificationResult(category=WasteCategory.RECYCLABLE, confidence=0.95)
        advice = advisor.advise(item, result)
        assert advice.category == WasteCategory.RECYCLABLE
        assert advice.bin_color == "blue"
        assert "High confidence" in advice.confidence_note

    def test_advise_low_confidence(self):
        advisor = RecyclingAdvisor()
        item = WasteItem(name="unknown item")
        result = ClassificationResult(category=WasteCategory.GENERAL, confidence=0.2)
        advice = advisor.advise(item, result)
        assert "Low confidence" in advice.confidence_note

    def test_alternatives_for_ewaste(self):
        advisor = RecyclingAdvisor()
        item = WasteItem(name="old phone")
        result = ClassificationResult(category=WasteCategory.E_WASTE, confidence=0.9)
        advice = advisor.advise(item, result)
        assert len(advice.alternatives) > 0

    def test_batch_advise(self):
        advisor = RecyclingAdvisor()
        pairs = [
            (WasteItem(name="bottle"), ClassificationResult(category=WasteCategory.RECYCLABLE, confidence=0.9)),
            (WasteItem(name="banana"), ClassificationResult(category=WasteCategory.ORGANIC, confidence=0.85)),
        ]
        results = advisor.batch_advise(pairs)
        assert len(results) == 2


class TestEnvironmentalImpact:
    def test_calculate_co2_saved(self):
        stream = _make_stream([
            _make_classified_item(WasteCategory.RECYCLABLE, weight=10.0),
        ])
        impact = EnvironmentalImpact()
        report = impact.calculate(stream)
        assert report.total_co2_saved_kg == 25.0  # 10 kg * 2.5

    def test_general_waste_no_savings(self):
        stream = _make_stream([
            _make_classified_item(WasteCategory.GENERAL, weight=5.0),
        ])
        impact = EnvironmentalImpact()
        report = impact.calculate(stream)
        assert report.total_co2_saved_kg == 0.0

    def test_trees_equivalent(self):
        stream = _make_stream([
            _make_classified_item(WasteCategory.RECYCLABLE, weight=10.0),
        ])
        impact = EnvironmentalImpact()
        report = impact.calculate(stream)
        assert report.trees_equivalent > 0

    def test_empty_stream(self):
        stream = _make_stream([])
        impact = EnvironmentalImpact()
        report = impact.calculate(stream)
        assert report.total_co2_saved_kg == 0.0
        assert report.trees_equivalent == 0.0
