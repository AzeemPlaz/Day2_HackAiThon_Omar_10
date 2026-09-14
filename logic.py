"""Pure business logic for EcoTrack. UI and database operations call these helpers."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from dataclasses import dataclass
from typing import Iterable, Sequence

CATEGORIES = ("Organic", "Plastic", "Paper", "E-waste", "Glass")
CATEGORY_TIPS = {
    "Organic": "Compost kitchen scraps or use a community composting route.",
    "Plastic": "Prefer refill packs, reusable containers, and segregate clean plastic.",
    "Paper": "Reuse one-sided paper and send clean paper to recycling.",
    "E-waste": "Never mix e-waste with general waste; use an authorised collection point.",
    "Glass": "Reuse jars where possible and keep glass separated for recycling.",
}


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def validate_record(record_date: str, category: str, weight_kg: float | str) -> float:
    parse_date(record_date)
    if category not in CATEGORIES:
        raise ValueError("Choose a valid waste category.")
    try:
        weight = float(weight_kg)
    except (TypeError, ValueError):
        raise ValueError("Weight must be a number.")
    if not 0 < weight <= 200:
        raise ValueError("Weight rejected. The value must be greater than 0 kg and no more than 200 kg.")
    return round(weight, 2)


@dataclass(frozen=True)
class WasteRecord:
    """A single household waste record required by the challenge."""
    item_id: int
    record_date: str
    category: str
    weight_kg: float
    recycled: bool


# Friendly alias used internally by the analytics helpers.
Record = WasteRecord


class Household:
    """Domain model representing a household/user-owned waste collection."""

    def __init__(self, household_id: int, name: str):
        self.household_id = household_id
        self.name = name

    def add_record(self, *args, **kwargs):
        """UI/application layer persists records; this method exists as the domain operation hook."""
        return {"action": "create", "args": args, "kwargs": kwargs}

    def update_record(self, item_id: int, **changes):
        return {"action": "update", "item_id": item_id, "changes": changes}

    def delete_record(self, item_id: int):
        return {"action": "delete", "item_id": item_id}

    def search(self, records: Sequence[Record], category: str | None = None):
        if not category or category == "All":
            return list(records)
        return [r for r in records if r.category == category]


class WasteReport:
    """Calculates explainable waste metrics for a selected period."""

    def __init__(self, records: Sequence[Record], start: date | None = None, end: date | None = None):
        self.records = [r for r in records if (start is None or parse_date(r.record_date) >= start) and (end is None or parse_date(r.record_date) <= end)]

    def total_waste(self) -> float:
        return round(sum(r.weight_kg for r in self.records), 2)

    def category_breakdown(self) -> dict[str, dict[str, float]]:
        totals: dict[str, float] = defaultdict(float)
        for r in self.records:
            totals[r.category] += r.weight_kg
        total = self.total_waste()
        return {
            category: {"kg": round(kg, 2), "percent": round((kg / total) * 100, 1) if total else 0.0}
            for category, kg in sorted(totals.items(), key=lambda x: -x[1])
        }

    def recycling_rate(self) -> float:
        total = self.total_waste()
        if total == 0:
            return 0.0
        recycled = sum(r.weight_kg for r in self.records if r.recycled)
        return round((recycled / total) * 100, 1)

    def sustainability_score(self) -> float:
        score = self.recycling_rate() * 0.7
        total = self.total_waste()
        if total:
            if total < 10:
                score += 30
            else:
                score += max(0, 30 - (total - 10))
        return round(min(score, 100), 1)

    def recommendations(self) -> list[str]:
        recs: list[str] = []
        breakdown = self.category_breakdown()
        rate = self.recycling_rate()
        if rate < 50:
            recs.append("Recycling rate is below 50% - separate clean paper, plastic and glass before disposal.")
        if breakdown:
            top_cat = next(iter(breakdown))
            if breakdown[top_cat]["percent"] > 40:
                recs.append(f"{top_cat} is the largest category at {breakdown[top_cat]['percent']}% - {CATEGORY_TIPS[top_cat]}")
        if not recs:
            recs.append("Great job! Your waste is well-recycled. Keep improving by reducing single-use items.")
        return recs

    def generate(self, household_name: str = "Household") -> dict:
        return {
            "household": household_name,
            "total_waste_kg": self.total_waste(),
            "category_breakdown": self.category_breakdown(),
            "recycling_rate_percent": self.recycling_rate(),
            "sustainability_score": self.sustainability_score(),
            "recommendations": self.recommendations(),
        }


def daily_series(records: Sequence[Record], days: int = 7) -> list[tuple[str, float, float]]:
    if not records:
        return []
    dates = [parse_date(r.record_date) for r in records]
    end = max(dates)
    start = end - timedelta(days=days - 1)
    series = []
    for idx in range(days):
        d = start + timedelta(days=idx)
        day_records = [r for r in records if parse_date(r.record_date) == d]
        recyclable = sum(r.weight_kg for r in day_records if r.recycled)
        other = sum(r.weight_kg for r in day_records if not r.recycled)
        series.append((d.strftime("%d %b"), round(recyclable, 2), round(other, 2)))
    return series


def reward_for_recycled_record(weight_kg: float) -> tuple[float, float]:
    """EcoTrack enhancement: 15 kg = 1 point = Rs 1."""
    points = round(weight_kg / 15.0, 2)
    return points, points
