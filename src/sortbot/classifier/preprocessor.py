"""Image preprocessing pipeline for the waste classifier."""

from __future__ import annotations

from pathlib import Path

import torch
from torchvision import transforms


class ImagePreprocessor:
    """Resize, normalize, and convert waste images to tensors.

    Default target size is 224x224 to match common CNN input dimensions.
    Normalization uses ImageNet statistics by default.
    """

    def __init__(
        self,
        target_size: tuple[int, int] = (224, 224),
        mean: tuple[float, float, float] = (0.485, 0.456, 0.406),
        std: tuple[float, float, float] = (0.229, 0.224, 0.225),
    ) -> None:
        self.target_size = target_size
        self.mean = mean
        self.std = std

        self._transform = transforms.Compose([
            transforms.Resize(target_size),
            transforms.CenterCrop(target_size[0]),
            transforms.ToTensor(),
            transforms.Normalize(mean=list(mean), std=list(std)),
        ])

        self._augmented_transform = transforms.Compose([
            transforms.Resize(int(target_size[0] * 1.15)),
            transforms.RandomCrop(target_size),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=list(mean), std=list(std)),
        ])

    def preprocess(self, image: "PIL.Image.Image") -> torch.Tensor:  # noqa: F821
        """Preprocess a PIL Image to a normalized tensor.

        Args:
            image: A PIL Image in RGB mode.

        Returns:
            Tensor of shape (3, H, W) ready for the classifier.
        """
        if image.mode != "RGB":
            image = image.convert("RGB")
        return self._transform(image)

    def preprocess_augmented(self, image: "PIL.Image.Image") -> torch.Tensor:  # noqa: F821
        """Preprocess with data augmentation (for training).

        Args:
            image: A PIL Image in RGB mode.

        Returns:
            Augmented tensor of shape (3, H, W).
        """
        if image.mode != "RGB":
            image = image.convert("RGB")
        return self._augmented_transform(image)

    def load_and_preprocess(self, path: str | Path) -> torch.Tensor:
        """Load an image from disk and preprocess it.

        Args:
            path: Path to an image file.

        Returns:
            Tensor of shape (1, 3, H, W) with batch dimension.
        """
        from PIL import Image

        image = Image.open(path).convert("RGB")
        tensor = self.preprocess(image)
        return tensor.unsqueeze(0)

    def denormalize(self, tensor: torch.Tensor) -> torch.Tensor:
        """Reverse normalization for visualization.

        Args:
            tensor: Normalized tensor of shape (3, H, W) or (B, 3, H, W).

        Returns:
            Denormalized tensor clamped to [0, 1].
        """
        mean = torch.tensor(self.mean).view(3, 1, 1)
        std = torch.tensor(self.std).view(3, 1, 1)

        if tensor.dim() == 4:
            mean = mean.unsqueeze(0)
            std = std.unsqueeze(0)

        return (tensor * std + mean).clamp(0, 1)
