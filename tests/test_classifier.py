"""Tests for the WasteClassifier CNN model."""

import torch

from sortbot.classifier.categories import WasteCategory
from sortbot.classifier.model import WasteClassifier
from sortbot.models import ClassificationResult


class TestWasteClassifier:
    def setup_method(self):
        self.model = WasteClassifier()
        self.model.eval()

    def test_forward_output_shape(self):
        x = torch.randn(2, 3, 224, 224)
        logits = self.model(x)
        assert logits.shape == (2, WasteCategory.count())

    def test_forward_single_image(self):
        x = torch.randn(1, 3, 224, 224)
        logits = self.model(x)
        assert logits.shape == (1, 6)

    def test_predict_returns_classification_result(self):
        x = torch.randn(1, 3, 224, 224)
        result = self.model.predict(x)
        assert isinstance(result, ClassificationResult)
        assert 0.0 <= result.confidence <= 1.0
        assert result.category in WasteCategory

    def test_predict_scores_sum_to_one(self):
        x = torch.randn(1, 3, 224, 224)
        result = self.model.predict(x)
        total = sum(result.scores.values())
        assert abs(total - 1.0) < 1e-4

    def test_predict_top_k(self):
        x = torch.randn(1, 3, 224, 224)
        top = self.model.predict_top_k(x, k=3)
        assert len(top) == 3
        # Scores should be descending.
        scores = [s for _, s in top]
        assert scores == sorted(scores, reverse=True)

    def test_num_classes(self):
        assert WasteClassifier.NUM_CLASSES == 6
