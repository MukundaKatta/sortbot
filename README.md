# SORTBOT - AI Waste Classifier

An AI-powered waste classification system that uses a CNN model to categorize waste
items into six categories and provides disposal guidance with environmental impact
analysis.

## Categories

| Category | Description |
|---|---|
| Recyclable | Plastics, metals, glass, paper products |
| Organic | Food scraps, yard waste, natural fibers |
| E-Waste | Electronics, batteries, cables |
| Hazardous | Chemicals, paints, medical waste |
| General | Non-recyclable, non-hazardous items |
| Compostable | Biodegradable materials suitable for composting |

## Installation

```bash
pip install -e .
```

## Usage

### CLI

```bash
# Classify a waste item image
sortbot classify image.jpg

# Run a simulated waste stream analysis
sortbot simulate --items 100

# Generate a waste composition report
sortbot report --format table
```

### Python API

```python
from sortbot.classifier.model import WasteClassifier
from sortbot.classifier.preprocessor import ImagePreprocessor

preprocessor = ImagePreprocessor()
classifier = WasteClassifier()

tensor = preprocessor.load_and_preprocess("waste_item.jpg")
result = classifier.predict(tensor)
print(result)
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Author

Mukunda Katta
