"""Tests for the ImagePreprocessor."""

import torch
from PIL import Image

from sortbot.classifier.preprocessor import ImagePreprocessor


class TestImagePreprocessor:
    def setup_method(self):
        self.preprocessor = ImagePreprocessor()

    def _make_image(self, width: int = 640, height: int = 480) -> Image.Image:
        return Image.new("RGB", (width, height), color=(128, 64, 32))

    def test_preprocess_output_shape(self):
        img = self._make_image()
        tensor = self.preprocessor.preprocess(img)
        assert tensor.shape == (3, 224, 224)

    def test_preprocess_converts_grayscale_to_rgb(self):
        img = Image.new("L", (100, 100), color=128)
        tensor = self.preprocessor.preprocess(img)
        assert tensor.shape == (3, 224, 224)

    def test_preprocess_augmented_output_shape(self):
        img = self._make_image()
        tensor = self.preprocessor.preprocess_augmented(img)
        assert tensor.shape == (3, 224, 224)

    def test_custom_target_size(self):
        preprocessor = ImagePreprocessor(target_size=(128, 128))
        img = self._make_image()
        tensor = preprocessor.preprocess(img)
        assert tensor.shape == (3, 128, 128)

    def test_denormalize_roundtrip(self):
        img = self._make_image()
        tensor = self.preprocessor.preprocess(img)
        denormed = self.preprocessor.denormalize(tensor)
        assert denormed.min() >= 0.0
        assert denormed.max() <= 1.0

    def test_denormalize_batch(self):
        img = self._make_image()
        tensor = self.preprocessor.preprocess(img).unsqueeze(0)  # (1, 3, 224, 224)
        denormed = self.preprocessor.denormalize(tensor)
        assert denormed.shape == (1, 3, 224, 224)
