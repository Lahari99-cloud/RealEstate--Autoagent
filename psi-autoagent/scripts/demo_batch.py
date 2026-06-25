import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


PROFILES = [
    "مرحبا, I need a 3BHK on Al Reem Island around 1.5M, ready to move. Chiller free preferred.",
    "Investment apartment on Yas Island, 2 bedrooms, AED 1.8M, post-handover payment plan.",
    "Looking for a family home in Masdar City, two bedrooms, budget 1.2 million, immediately.",
]


client = TestClient(app)
for inquiry in PROFILES:
    created = client.post("/v1/proposals", json={"inquiry": inquiry, "require_approval": True}).json()
    completed = client.post(created["approval_url"], json={"approved": True, "reviewer": "Live Demo"}).json()
    print({"run_id": completed["run_id"], "status": completed["status"], "lead": completed["lead"],
           "top_match": completed["recommendations"][0]["listing"]["title"], "pdf": completed["pdf_url"]})
