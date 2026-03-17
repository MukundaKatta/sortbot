"""Synthetic classification data generator for testing and demos."""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from sortbot.classifier.categories import WasteCategory
from sortbot.models import ClassificationResult, ClassifiedItem, WasteItem, WasteStream


# Probability distribution across categories (sums to 1.0).
_DEFAULT_DISTRIBUTION: dict[WasteCategory, float] = {
    WasteCategory.RECYCLABLE: 0.30,
    WasteCategory.ORGANIC: 0.25,
    WasteCategory.COMPOSTABLE: 0.10,
    WasteCategory.GENERAL: 0.20,
    WasteCategory.E_WASTE: 0.08,
    WasteCategory.HAZARDOUS: 0.07,
}

# Typical weight ranges in kg per category.
_WEIGHT_RANGES: dict[WasteCategory, tuple[float, float]] = {
    WasteCategory.RECYCLABLE: (0.01, 1.5),
    WasteCategory.ORGANIC: (0.05, 2.0),
    WasteCategory.COMPOSTABLE: (0.02, 1.0),
    WasteCategory.GENERAL: (0.01, 0.8),
    WasteCategory.E_WASTE: (0.1, 5.0),
    WasteCategory.HAZARDOUS: (0.05, 3.0),
}

_SOURCES = ["kitchen", "office", "garage", "bathroom", "garden", "workshop"]


def generate_item(
    category: WasteCategory | None = None,
    *,
    seed: int | None = None,
) -> ClassifiedItem:
    """Generate a single synthetic classified waste item.

    Args:
        category: Force a specific category, or None for random.
        seed: Optional random seed for reproducibility.

    Returns:
        A ClassifiedItem with synthetic data.
    """
    if seed is not None:
        random.seed(seed)

    if category is None:
        categories = list(_DEFAULT_DISTRIBUTION.keys())
        weights = list(_DEFAULT_DISTRIBUTION.values())
        category = random.choices(categories, weights=weights, k=1)[0]

    examples = category.examples
    name = random.choice(examples)
    weight_lo, weight_hi = _WEIGHT_RANGES[category]

    item = WasteItem(
        name=name,
        source=random.choice(_SOURCES),
        weight_kg=round(random.uniform(weight_lo, weight_hi), 3),
        timestamp=datetime.now() - timedelta(hours=random.randint(0, 720)),
    )

    # Simulate confidence: usually high, occasionally low.
    confidence = min(1.0, max(0.1, random.gauss(0.82, 0.12)))
    remaining = 1.0 - confidence
    scores: dict[str, float] = {}
    other_cats = [c for c in WasteCategory if c != category]
    random_splits = [random.random() for _ in other_cats]
    total_splits = sum(random_splits)
    for cat, split in zip(other_cats, random_splits):
        scores[cat.value] = round((split / total_splits) * remaining, 4)
    scores[category.value] = round(confidence, 4)

    result = ClassificationResult(
        category=category,
        confidence=round(confidence, 4),
        scores=scores,
    )

    return ClassifiedItem(item=item, result=result)


def generate_stream(
    n_items: int = 100,
    stream_name: str = "simulated",
    *,
    seed: int | None = None,
    distribution: dict[WasteCategory, float] | None = None,
) -> WasteStream:
    """Generate a synthetic waste stream with n classified items.

    Args:
        n_items: Number of items to generate.
        stream_name: Name for the waste stream.
        seed: Optional random seed for reproducibility.
        distribution: Optional custom probability distribution across categories.

    Returns:
        A WasteStream populated with synthetic ClassifiedItems.
    """
    if seed is not None:
        random.seed(seed)

    dist = distribution or _DEFAULT_DISTRIBUTION

    categories = list(dist.keys())
    weights = list(dist.values())

    items: list[ClassifiedItem] = []
    for _ in range(n_items):
        cat = random.choices(categories, weights=weights, k=1)[0]
        items.append(generate_item(category=cat))

    return WasteStream(name=stream_name, items=items)
