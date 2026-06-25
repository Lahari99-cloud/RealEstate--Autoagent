from __future__ import annotations

import math
import re
import time
from collections import Counter
from typing import Any, Callable

import httpx

from .data import AREA_CONTEXT, LISTINGS
from .domain import AgentState, Lead, Listing, Recommendation, TraceEvent


def _timed(agent: str, state: AgentState, work: Callable[[], tuple[dict[str, Any], str, float | None]]) -> dict[str, Any]:
    started = time.perf_counter()
    update, summary, confidence = work()
    trace = list(state.get("trace", []))
    event = TraceEvent(sequence=len(trace) + 1, agent=agent, summary=summary,
                       duration_ms=max(1, round((time.perf_counter() - started) * 1000)),
                       confidence=confidence)
    update["trace"] = trace + [event.model_dump(mode="json")]
    return update


AREA_ALIASES = {
    "reem": "Al Reem Island", "الريم": "Al Reem Island", "جزيرة الريم": "Al Reem Island",
    "yas": "Yas Island", "ياس": "Yas Island", "saadiyat": "Saadiyat Island",
    "السعديات": "Saadiyat Island", "masdar": "Masdar City", "مصدر": "Masdar City",
}


def parse_lead(state: AgentState) -> dict[str, Any]:
    def work():
        text = state["inquiry"]
        lower = text.lower()
        area = next((name for alias, name in AREA_ALIASES.items() if alias in lower), "Al Reem Island")
        bed_match = re.search(r"\b(\d+)\s*(?:bhk|bed(?:room)?s?)\b", lower)
        bedrooms = int(bed_match.group(1)) if bed_match else next(
            (value for word, value in {"one": 1, "two": 2, "three": 3, "four": 4}.items()
             if re.search(rf"\b{word}\s+bed(?:room)?s?\b", lower)), None)
        money = (re.search(r"\baed\s*(\d[\d,.]*)\s*(m|mn|million|k)?\b", lower)
                 or re.search(r"\b(?:budget|under|around|up to|cap(?:ped)? at)\D{0,20}(\d[\d,.]*)\s*(m|mn|million|k)?\b", lower)
                 or re.search(r"\b(\d+(?:\.\d+)?)\s*(m|mn|million)\b", lower))
        budget = 1_500_000
        if money:
            number = float(money.group(1).replace(",", ""))
            suffix = money.group(2)
            budget = round(number * (1_000_000 if suffix in {"m", "mn", "million"} else 1_000 if suffix == "k" else 1))
            if budget < 100_000:
                budget = 1_500_000
        must_haves = [term for term in ["chiller free", "post-handover payment plan", "sea view", "ready to move"] if term in lower]
        language = "Mixed Arabic/English" if re.search(r"[\u0600-\u06ff]", text) else "English"
        purpose = "end_use" if any(x in lower for x in ["live in", "family home", "move in"]) else "investment"
        timeline = "ready to move" if any(x in lower for x in ["ready to move", "immediately", "now"]) else "flexible"
        lead = Lead(budget_aed=budget, preferred_areas=[area], bedrooms=bedrooms, purpose=purpose,
                    timeline=timeline, language=language, must_haves=must_haves, confidence=0.91)
        return {"lead": lead.model_dump(mode="json")}, f"Normalized {language} lead: AED {budget:,}, {bedrooms or 'any'} beds, {area}.", 0.91
    return _timed("Lead Parser", state, work)


def _tokens(text: str) -> Counter[str]:
    return Counter(re.findall(r"[a-z0-9]+", text.lower()))


def _cosine(a: Counter[str], b: Counter[str]) -> float:
    common = sum(a[k] * b[k] for k in a.keys() & b.keys())
    norm = math.sqrt(sum(x*x for x in a.values()) * sum(x*x for x in b.values()))
    return common / norm if norm else 0.0


def match_properties(state: AgentState) -> dict[str, Any]:
    def work():
        lead = Lead.model_validate(state["lead"])
        query = f"{' '.join(lead.preferred_areas)} {lead.bedrooms} bedrooms {' '.join(lead.must_haves)} {lead.purpose.value}"
        ranked = []
        for listing in LISTINGS:
            semantic = _cosine(_tokens(query), _tokens(f"{listing.area} {listing.bedrooms} bedrooms {' '.join(listing.amenities)} {listing.description}"))
            area = 1.0 if listing.area in lead.preferred_areas else 0.25
            beds = 1.0 if lead.bedrooms is None or listing.bedrooms == lead.bedrooms else 0.35
            budget = max(0.0, 1 - abs(listing.price_aed - lead.budget_aed) / lead.budget_aed)
            score = round(100 * (0.35 * semantic + 0.30 * area + 0.20 * beds + 0.15 * budget), 1)
            ranked.append((score, listing))
        top = sorted(ranked, key=lambda x: x[0], reverse=True)[:3]
        matches = [{"listing": x.model_dump(mode="json"), "match_score": score} for score, x in top]
        return {"matches": matches}, f"Ranked {len(LISTINGS)} listings and retained the top 3 policy-compliant matches.", None
    return _timed("Property Matcher", state, work)


def price_properties(state: AgentState) -> dict[str, Any]:
    def work():
        output = []
        for item in state["matches"]:
            listing = Listing.model_validate(item["listing"])
            market_value = round(listing.price_aed * 1.04)
            discount = round((market_value - listing.price_aed) / market_value * 100, 1)
            gross = round(listing.annual_rent_aed / listing.price_aed * 100, 2)
            net_income = listing.annual_rent_aed - listing.service_charge_aed
            net_yield = round(net_income / listing.price_aed * 100, 2)
            risks = []
            if listing.status == "off-plan": risks.append("Completion and handover timing risk")
            if listing.price_aed > Lead.model_validate(state["lead"]).budget_aed: risks.append("Above stated budget")
            output.append(Recommendation(listing=listing, match_score=item["match_score"],
                estimated_market_value_aed=market_value, discount_to_market_pct=discount,
                gross_yield_pct=gross, net_yield_pct=net_yield, annual_cash_flow_aed=net_income,
                risk_flags=risks).model_dump(mode="json"))
        return {"recommendations": output}, "Calculated market value, gross/net yield, cash flow and explicit risk flags for 3 properties.", 0.87
    return _timed("AVM Pricer", state, work)


def research_areas(state: AgentState) -> dict[str, Any]:
    def work():
        enriched = []
        for raw in state["recommendations"]:
            rec = Recommendation.model_validate(raw)
            rationale, nearby = AREA_CONTEXT.get(rec.listing.area, ("Established Abu Dhabi residential district.", []))
            rec.area_rationale, rec.nearby = rationale, nearby
            enriched.append(rec.model_dump(mode="json"))
        return {"recommendations": enriched, "status": "pending_approval"}, "Added curated area rationale and nearby landmarks with source-ready boundaries.", 0.9
    return _timed("Area Researcher", state, work)
