"""CNN model for waste image classification into 6 categories."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from sortbot.classifier.categories import WasteCategory
from sortbot.models import ClassificationResult


class WasteClassifier(nn.Module):
    """Convolutional neural network for classifying waste images.

    Architecture: 4 convolutional blocks followed by fully connected layers.
    Input: RGB image tensor of shape (B, 3, 224, 224).
    Output: logits for 6 waste categories.
    """

    NUM_CLASSES = WasteCategory.count()

    def __init__(self, dropout: float = 0.3) -> None:
        super().__init__()

        self.features = nn.Sequential(
            # Block 1: 3 -> 32 channels
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            # Block 2: 32 -> 64 channels
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            # Block 3: 64 -> 128 channels
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            # Block 4: 128 -> 256 channels
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4)),
        )

        self.classifier_head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(512, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(128, self.NUM_CLASSES),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning raw logits.

        Args:
            x: Input tensor of shape (B, 3, 224, 224).

        Returns:
            Logits tensor of shape (B, NUM_CLASSES).
        """
        x = self.features(x)
        x = self.classifier_head(x)
        return x

    @torch.no_grad()
    def predict(self, x: torch.Tensor) -> ClassificationResult:
        """Classify a single image tensor and return a structured result.

        Args:
            x: Preprocessed tensor of shape (1, 3, 224, 224).

        Returns:
            ClassificationResult with predicted category and confidence scores.
        """
        self.eval()
        logits = self.forward(x)
        probabilities = F.softmax(logits, dim=1).squeeze(0)

        predicted_index = int(torch.argmax(probabilities).item())
        category = WasteCategory.from_index(predicted_index)
        confidence = float(probabilities[predicted_index].item())

        category_scores = {
            WasteCategory.from_index(i).value: float(probabilities[i].item())
            for i in range(self.NUM_CLASSES)
        }

        return ClassificationResult(
            category=category,
            confidence=confidence,
            scores=category_scores,
        )

    @torch.no_grad()
    def predict_top_k(self, x: torch.Tensor, k: int = 3) -> list[tuple[WasteCategory, float]]:
        """Return top-k predicted categories with their confidence scores.

        Args:
            x: Preprocessed tensor of shape (1, 3, 224, 224).
            k: Number of top predictions to return.

        Returns:
            List of (category, confidence) tuples sorted by confidence descending.
        """
        self.eval()
        logits = self.forward(x)
        probabilities = F.softmax(logits, dim=1).squeeze(0)

        top_values, top_indices = torch.topk(probabilities, k)
        return [
            (WasteCategory.from_index(int(idx.item())), float(val.item()))
            for val, idx in zip(top_values, top_indices)
        ]
