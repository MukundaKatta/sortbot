"""Environmental impact calculations for proper waste sorting."""

from __future__ import annotations

from dataclasses import dataclass

from sortbot.classifier.categories import WasteCategory
from sortbot.models import WasteStream


# Approximate CO2 savings in kg per kg of waste properly sorted (vs. landfill).
# Sources: EPA / DEFRA / lifecycle analysis averages.
_CO2_SAVINGS_PER_KG: dict[WasteCategory, float] = {
    WasteCategory.RECYCLABLE: 2.5,     # Recycling avoids virgin material extraction
    WasteCategory.ORGANIC: 0.6,        # Composting vs. methane from landfill
    WasteCategory.E_WASTE: 5.0,        # Precious metal recovery
    WasteCategory.HAZARDOUS: 1.0,      # Proper treatment vs. soil/water contamination
    WasteCategory.GENERAL: 0.0,        # Baseline landfill -- no savings
    WasteCategory.COMPOSTABLE: 0.5,    # Similar to organic
}

# Approximate water savings in liters per kg of waste properly sorted.
_WATER_SAVINGS_PER_KG: dict[WasteCategory, float] = {
    WasteCategory.RECYCLABLE: 20.0,
    WasteCategory.ORGANIC: 5.0,
    WasteCategory.E_WASTE: 30.0,
    WasteCategory.HAZARDOUS: 10.0,
    WasteCategory.GENERAL: 0.0,
    WasteCategory.COMPOSTABLE: 4.0,
}


@dataclass
class ImpactReport:
    """Summary of environmental impact from proper waste sorting."""

    total_co2_saved_kg: float
    total_water_saved_liters: float
    co2_by_category: dict[WasteCategory, float]
    water_by_category: dict[WasteCategory, float]
    trees_equivalent: float
    driving_km_equivalent: float

    @property
    def total_co2_saved_tonnes(self) -> float:
        return self.total_co2_saved_kg / 1000.0


class EnvironmentalImpact:
    """Calculate the environmental benefit of sorting waste correctly.

    Uses category-level CO2 and water savings factors applied to the
    weight of items in a waste stream.
    """

    # Average CO2 absorbed by one tree per year (kg).
    KG_CO2_PER_TREE_YEAR = 22.0

    # Average CO2 per km driven (kg).
    KG_CO2_PER_KM_DRIVEN = 0.21

    def __init__(
        self,
        co2_factors: dict[WasteCategory, float] | None = None,
        water_factors: dict[WasteCategory, float] | None = None,
    ) -> None:
        self.co2_factors = co2_factors or _CO2_SAVINGS_PER_KG
        self.water_factors = water_factors or _WATER_SAVINGS_PER_KG

    def calculate(self, stream: WasteStream) -> ImpactReport:
        """Calculate environmental impact for a waste stream.

        Args:
            stream: A WasteStream with classified items.

        Returns:
            An ImpactReport with CO2 and water savings.
        """
        weight_breakdown = stream.category_weight_breakdown()

        co2_by_category: dict[WasteCategory, float] = {}
        water_by_category: dict[WasteCategory, float] = {}

        for category, weight in weight_breakdown.items():
            co2_by_category[category] = weight * self.co2_factors.get(category, 0.0)
            water_by_category[category] = weight * self.water_factors.get(category, 0.0)

        total_co2 = sum(co2_by_category.values())
        total_water = sum(water_by_category.values())

        return ImpactReport(
            total_co2_saved_kg=round(total_co2, 3),
            total_water_saved_liters=round(total_water, 3),
            co2_by_category=co2_by_category,
            water_by_category=water_by_category,
            trees_equivalent=round(total_co2 / self.KG_CO2_PER_TREE_YEAR, 2) if total_co2 > 0 else 0.0,
            driving_km_equivalent=round(total_co2 / self.KG_CO2_PER_KM_DRIVEN, 2) if total_co2 > 0 else 0.0,
        )
