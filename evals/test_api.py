from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.data import LISTINGS
from backend.app.main import app


client = TestClient(app)


def test_real_psi_inventory_is_loaded_from_data_folder():
    assert len(LISTINGS) == 109
    assert any(listing.id == "AP23285" for listing in LISTINGS)
    assert any(listing.area == "Yas Island" for listing in LISTINGS)


def test_mixed_language_lead_pauses_then_generates_pdf():
    inquiry = "مرحبا, I am looking for a 3BHK on Al Reem Island. My budget is 1.5M. Ready to move in. Shukran."
    created = client.post("/v1/proposals", json={"inquiry": inquiry, "require_approval": True})
    assert created.status_code == 202
    data = created.json()
    assert data["status"] == "pending_approval"
    assert data["lead"]["budget_aed"] == 1_500_000
    assert data["lead"]["bedrooms"] == 3
    assert data["lead"]["language"] == "Mixed Arabic/English"
    assert data["qualification"]["score"] >= 70
    assert data["qualification"]["crm_stage"] in {"marketing-qualified lead", "sales-qualified lead"}
    assert data["compliance"]["risk_level"] in {"standard", "review_required"}
    assert data["compliance"]["required_checks"]
    assert len(data["recommendations"]) == 3
    assert data["recommendations"][0]["monthly_payment_aed"] > 0
    assert data["recommendations"][0]["income_required_aed"] > 0
    assert "affordability" in data["recommendations"][0]["affordability_note"].lower() or data["recommendations"][0]["affordability_note"]
    assert len(data["trace"]) == 7
    assert [event["agent"] for event in data["trace"]] == [
        "Lead Parser",
        "Lead Qualification Agent",
        "Property Matcher",
        "AVM Pricer",
        "Mortgage & Affordability Agent",
        "Area Researcher",
        "RERA / Compliance Agent",
    ]

    approved = client.post(data["approval_url"], json={"approved": True, "reviewer": "Demo Agent", "note": "Verified"})
    result = approved.json()
    assert result["status"] == "completed"
    pdf = client.get(result["pdf_url"])
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")
    assert len(pdf.content) > 3000


def test_rejection_prevents_pdf():
    created = client.post("/v1/proposals", json={"inquiry": "Need a 2 bedroom investment on Yas Island under AED 1.8M", "require_approval": True}).json()
    rejected = client.post(created["approval_url"], json={"approved": False, "reviewer": "Risk Officer", "note": "Re-price"}).json()
    assert rejected["status"] == "rejected"
    assert rejected["pdf_url"] is None


def test_budget_and_word_bedrooms_are_not_confused():
    yas = client.post("/v1/proposals", json={"inquiry": "Investment on Yas Island, 2 bedrooms, AED 1.8M", "require_approval": True}).json()
    assert yas["lead"]["budget_aed"] == 1_800_000
    assert yas["lead"]["bedrooms"] == 2
    masdar = client.post("/v1/proposals", json={"inquiry": "Family home in Masdar City, two bedrooms, budget 1.2 million", "require_approval": True}).json()
    assert masdar["lead"]["budget_aed"] == 1_200_000
    assert masdar["lead"]["bedrooms"] == 2


def test_memory_observability_evaluation_and_hindi_support():
    created = client.post("/v1/proposals", json={
        "conversation_id": "demo-buyer-1",
        "inquiry": "Need 2BHK on Yas Island. मेरा budget AED 1.8M है और mortgage चाहिए.",
        "require_approval": True,
    }).json()
    assert created["conversation_id"] == "demo-buyer-1"
    assert created["lead"]["language"] == "Mixed Hindi/English"
    assert created["lead"]["bedrooms"] == 2
    assert created["qualification"]["financing_readiness"] == "mentioned"

    conversation = client.get("/v1/conversations/demo-buyer-1").json()
    assert len(conversation) >= 2
    assert conversation[0]["role"] == "buyer"

    metrics = client.get("/v1/observability/metrics").json()
    assert metrics["conversation_count"] >= 1
    assert metrics["agent_call_counts"]["RERA / Compliance Agent"] >= 1

    dashboard = client.get("/v1/evaluations/dashboard").json()
    assert dashboard["status"] == "foundation"
    assert "golden inquiry dataset" in dashboard["planned_checks"]
