"""SORTBOT command-line interface."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(package_name="sortbot")
def cli() -> None:
    """SORTBOT - AI Waste Classifier.

    Classify waste items into categories and get disposal guidance.
    """


@cli.command()
@click.argument("image_path", type=click.Path(exists=True, path_type=Path))
@click.option("--top-k", default=3, help="Number of top predictions to show.")
def classify(image_path: Path, top_k: int) -> None:
    """Classify a waste item from an image."""
    import torch

    from sortbot.classifier.model import WasteClassifier
    from sortbot.classifier.preprocessor import ImagePreprocessor

    preprocessor = ImagePreprocessor()
    model = WasteClassifier()
    model.eval()

    console.print(f"[bold]Classifying:[/bold] {image_path}")

    tensor = preprocessor.load_and_preprocess(image_path)
    result = model.predict(tensor)

    console.print(f"\n  Category: [bold green]{result.category.value.capitalize()}[/bold green]")
    console.print(f"  Confidence: {result.confidence:.2%}")
    console.print(f"  Bin: {result.category.bin_color}")
    console.print(f"\n  [bold]Disposal:[/bold] {result.disposal_instructions}")

    if top_k > 1:
        top_predictions = model.predict_top_k(tensor, k=top_k)
        console.print(f"\n  [bold]Top {top_k} predictions:[/bold]")
        for cat, score in top_predictions:
            console.print(f"    {cat.value.capitalize():15s} {score:.2%}")


@cli.command()
@click.option("--items", "-n", default=100, help="Number of items to simulate.")
@click.option("--seed", "-s", default=None, type=int, help="Random seed.")
def simulate(items: int, seed: int | None) -> None:
    """Run a simulated waste stream classification."""
    from sortbot.report import ReportGenerator
    from sortbot.simulator import generate_stream

    console.print(f"[bold]Simulating {items} waste items...[/bold]\n")
    stream = generate_stream(n_items=items, seed=seed)
    reporter = ReportGenerator(console=console)
    reporter.print_full_report(stream)


@cli.command()
@click.option("--items", "-n", default=50, help="Number of items to simulate for the report.")
@click.option("--seed", "-s", default=None, type=int, help="Random seed.")
@click.option(
    "--format", "fmt",
    type=click.Choice(["table", "summary"]),
    default="table",
    help="Report format.",
)
def report(items: int, seed: int | None, fmt: str) -> None:
    """Generate a waste composition report."""
    from sortbot.report import ReportGenerator
    from sortbot.simulator import generate_stream

    stream = generate_stream(n_items=items, seed=seed)
    reporter = ReportGenerator(console=console)

    if fmt == "table":
        reporter.print_full_report(stream)
    else:
        from sortbot.analyzer.composition import WasteCompositionAnalyzer
        from sortbot.analyzer.impact import EnvironmentalImpact

        analyzer = WasteCompositionAnalyzer(stream)
        impact_calc = EnvironmentalImpact()
        impact_report = impact_calc.calculate(stream)

        console.print(f"[bold]Stream:[/bold] {stream.name}")
        console.print(f"[bold]Items:[/bold] {stream.total_items}")
        console.print(f"[bold]Weight:[/bold] {stream.total_weight_kg:.2f} kg")
        console.print(f"[bold]Diversion Rate:[/bold] {analyzer.diversion_rate():.1f}%")
        console.print(f"[bold]CO2 Saved:[/bold] {impact_report.total_co2_saved_kg:.2f} kg")
        console.print(f"[bold]Water Saved:[/bold] {impact_report.total_water_saved_liters:.1f} L")


@cli.command()
@click.argument("category", type=click.Choice([c.value for c in _get_categories()]))
def info(category: str) -> None:
    """Show disposal instructions for a waste category."""
    from sortbot.classifier.categories import WasteCategory

    cat = WasteCategory(category)
    console.print(f"\n[bold]{cat.value.capitalize()}[/bold] (bin: {cat.bin_color})")
    console.print(f"\n  {cat.disposal_instructions}")
    console.print(f"\n  [bold]Examples:[/bold] {', '.join(cat.examples)}\n")


def _get_categories() -> list:
    """Lazy import to avoid circular dependency at module level."""
    from sortbot.classifier.categories import WasteCategory
    return list(WasteCategory)
