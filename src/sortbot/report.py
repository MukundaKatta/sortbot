"""Report generation for waste stream analysis."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sortbot.analyzer.composition import WasteCompositionAnalyzer
from sortbot.analyzer.impact import EnvironmentalImpact
from sortbot.classifier.categories import WasteCategory
from sortbot.models import WasteStream


class ReportGenerator:
    """Generate rich-formatted reports for waste stream analysis."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def print_composition_report(self, stream: WasteStream) -> None:
        """Print a composition breakdown table for a waste stream."""
        analyzer = WasteCompositionAnalyzer(stream)
        counts = analyzer.item_count_by_category()
        percentages = analyzer.percentage_by_category()
        weights = analyzer.weight_by_category()

        table = Table(title=f"Waste Composition: {stream.name}", show_lines=True)
        table.add_column("Category", style="bold")
        table.add_column("Bin", justify="center")
        table.add_column("Items", justify="right")
        table.add_column("% Items", justify="right")
        table.add_column("Weight (kg)", justify="right")

        for cat in WasteCategory:
            count = counts.get(cat, 0)
            pct = percentages.get(cat, 0.0)
            weight = weights.get(cat, 0.0)
            table.add_row(
                cat.value.capitalize(),
                f"[{cat.bin_color}]{cat.bin_color}[/{cat.bin_color}]",
                str(count),
                f"{pct:.1f}%",
                f"{weight:.2f}",
            )

        table.add_row(
            "[bold]Total[/bold]", "",
            str(stream.total_items),
            "100.0%",
            f"{stream.total_weight_kg:.2f}",
        )

        self.console.print(table)

        diversion = analyzer.diversion_rate()
        self.console.print(f"\n  Diversion Rate: [bold green]{diversion:.1f}%[/bold green]")
        self.console.print(f"  Average Confidence: [bold]{stream.average_confidence():.2f}[/bold]\n")

        flags = analyzer.contamination_flags()
        if flags:
            self.console.print(Panel("\n".join(f"  * {f}" for f in flags), title="Warnings", border_style="yellow"))

    def print_impact_report(self, stream: WasteStream) -> None:
        """Print an environmental impact report for a waste stream."""
        impact_calc = EnvironmentalImpact()
        report = impact_calc.calculate(stream)

        table = Table(title="Environmental Impact (Proper Sorting vs. Landfill)", show_lines=True)
        table.add_column("Category", style="bold")
        table.add_column("CO2 Saved (kg)", justify="right")
        table.add_column("Water Saved (L)", justify="right")

        for cat in WasteCategory:
            co2 = report.co2_by_category.get(cat, 0.0)
            water = report.water_by_category.get(cat, 0.0)
            if co2 > 0 or water > 0:
                table.add_row(cat.value.capitalize(), f"{co2:.2f}", f"{water:.1f}")

        table.add_row(
            "[bold]Total[/bold]",
            f"[bold green]{report.total_co2_saved_kg:.2f}[/bold green]",
            f"[bold cyan]{report.total_water_saved_liters:.1f}[/bold cyan]",
        )

        self.console.print(table)
        self.console.print(f"\n  Equivalent to [bold]{report.trees_equivalent}[/bold] trees absorbing CO2 for a year")
        self.console.print(f"  Equivalent to [bold]{report.driving_km_equivalent} km[/bold] not driven\n")

    def print_full_report(self, stream: WasteStream) -> None:
        """Print both composition and impact reports."""
        self.console.print(Panel("[bold]SORTBOT Waste Analysis Report[/bold]", border_style="bright_blue"))
        self.console.print()
        self.print_composition_report(stream)
        self.console.print()
        self.print_impact_report(stream)
