from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .domain import Listing


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PSI_LISTINGS_PATH = PROJECT_ROOT / "data" / "psi_listings.json"


AREA_CONTEXT = {
    "Al Reem Island": ("A mature waterfront investment district with deep rental demand from professionals and families.",
                       ["Reem Mall", "Sorbonne University Abu Dhabi", "Galleria Mall - 10 min"]),
    "Yas Island": ("A leisure and employment hub supported by tourism, entertainment and airport connectivity.",
                   ["Yas Mall", "Yas Marina Circuit", "Zayed International Airport - 15 min"]),
    "Saadiyat Island": ("Abu Dhabi's premium culture and beach district, suited to capital-growth buyers.",
                        ["Louvre Abu Dhabi", "Cranleigh Abu Dhabi", "Saadiyat Beach"]),
    "Masdar City": ("A sustainability-led business district with accessible entry prices and resilient tenant demand.",
                    ["Masdar City Free Zone", "Zayed International Airport", "My City Centre Masdar"]),
    "Al Raha Beach": ("A waterfront residential corridor with strong family appeal and airport access.",
                      ["Al Raha Mall", "Yas Island - 10 min", "Zayed International Airport - 15 min"]),
    "Zayed City": ("A master-planned growth corridor with family communities and newer supply.",
                   ["Abu Dhabi International Airport corridor", "Schools and parks", "Future residential infrastructure"]),
    "Al Shamkhah": ("A villa-led residential area with larger layouts and end-user demand from UAE families.",
                    ["Abu Dhabi city access", "Community retail", "Family parks"]),
}


FALLBACK_LISTINGS = [
    Listing(id="PSI-RE-001", title="Canal View Residence", area="Al Reem Island", bedrooms=3,
            price_aed=1_480_000, size_sqft=1680, annual_rent_aed=112_000, service_charge_aed=18_500,
            status="ready", amenities=["pool", "gym", "chiller free", "canal view"],
            description="Ready three-bedroom home with strong family rental demand near Reem Mall."),
    Listing(id="PSI-YAS-001", title="Yas Golf Collection", area="Yas Island", bedrooms=2,
            price_aed=1_720_000, size_sqft=1280, annual_rent_aed=125_000, service_charge_aed=19_500,
            status="off-plan", amenities=["golf view", "pool", "post-handover plan"],
            description="Investor-oriented resort apartment close to Yas attractions."),
    Listing(id="PSI-MBJ-001", title="Masdar Green Living", area="Masdar City", bedrooms=2,
            price_aed=1_180_000, size_sqft=1210, annual_rent_aed=91_000, service_charge_aed=13_500,
            status="ready", amenities=["sustainable", "metro access", "pool"],
            description="Energy-efficient residence serving airport and free-zone professionals."),
]


AREA_RENT_YIELD = {
    "Al Reem Island": 0.067,
    "Yas Island": 0.064,
    "Saadiyat Island": 0.052,
    "Masdar City": 0.069,
    "Al Raha Beach": 0.061,
    "Zayed City": 0.055,
    "Al Shamkhah": 0.050,
}


SERVICE_CHARGE_PER_SQFT = {
    "Apartment": 15,
    "Studio": 14,
    "Duplex": 12,
    "Townhouse": 6,
    "Villa": 5,
    "Plot": 1,
    "Residential Land": 1,
}


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _infer_status(raw: dict[str, Any]) -> str:
    text = " ".join(str(raw.get(field, "")) for field in ("title", "project", "view", "furnish")).lower()
    if any(term in text for term in ("handover", "off plan", "off-plan", "post-handover", "by ")):
        return "off-plan"
    if any(term in text for term in ("ready", "resale", "move in")):
        return "ready"
    return "ready"


def _amenities(raw: dict[str, Any]) -> list[str]:
    terms = []
    text = " ".join(str(raw.get(field, "")) for field in ("title", "project", "community", "view", "furnish")).lower()
    for keyword in (
        "balcony", "sea view", "canal view", "marina view", "golf", "pool", "garden",
        "high floor", "corner", "maid", "furnished", "luxury", "prime location",
        "kitchen appliances", "community view", "park view",
    ):
        if keyword in text:
            terms.append(keyword)
    if raw.get("view"):
        view = str(raw["view"]).strip().lower()
        if view and view not in terms:
            terms.append(view)
    return terms or ["community amenities"]


def _description(raw: dict[str, Any]) -> str:
    project = str(raw.get("project") or "PSI selected property")
    community = str(raw.get("community") or "Abu Dhabi")
    developer = str(raw.get("developer") or "leading developer")
    property_type = str(raw.get("type") or "property")
    view = str(raw.get("view") or "community setting")
    return f"{property_type} in {project}, {community}, by {developer}, with {view}."


def _estimate_annual_rent(raw: dict[str, Any]) -> int:
    price = _as_int(raw.get("price_aed"))
    area = str(raw.get("community") or "")
    property_type = str(raw.get("type") or "")
    yield_rate = AREA_RENT_YIELD.get(area, 0.058)
    if property_type in {"Villa", "Townhouse"}:
        yield_rate -= 0.006
    if property_type in {"Studio", "Apartment"} and _as_int(raw.get("beds")) <= 1:
        yield_rate += 0.006
    return max(24_000, round(price * yield_rate / 1000) * 1000)


def _estimate_service_charge(raw: dict[str, Any]) -> int:
    sqft = max(_as_int(raw.get("sqft")), 350)
    property_type = str(raw.get("type") or "Apartment")
    rate = SERVICE_CHARGE_PER_SQFT.get(property_type, 10)
    return round(sqft * rate)


def _to_listing(raw: dict[str, Any]) -> Listing | None:
    price = _as_int(raw.get("price_aed"))
    if price <= 0:
        return None
    ref = str(raw.get("ref") or raw.get("id") or "PSI")
    return Listing(
        id=ref,
        title=str(raw.get("title") or raw.get("project") or ref),
        area=str(raw.get("community") or "Abu Dhabi"),
        bedrooms=max(0, _as_int(raw.get("beds"))),
        price_aed=price,
        size_sqft=max(_as_int(raw.get("sqft")), 350),
        annual_rent_aed=_estimate_annual_rent(raw),
        service_charge_aed=_estimate_service_charge(raw),
        status=_infer_status(raw),
        amenities=_amenities(raw),
        description=_description(raw),
    )


def load_psi_listings(path: Path = PSI_LISTINGS_PATH) -> list[Listing]:
    """Load the PSI-style inventory from data/psi_listings.json.

    The raw export does not include rental income, service charges, or listing
    prose, so this adapter derives conservative demo values for the AVM and
    proposal writer while preserving the original property identity and price.
    """
    try:
        raw_items = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return FALLBACK_LISTINGS

    listings = [_to_listing(item) for item in raw_items if isinstance(item, dict)]
    valid_listings = [listing for listing in listings if listing is not None]
    return valid_listings or FALLBACK_LISTINGS


LISTINGS = load_psi_listings()
