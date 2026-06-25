# Demo Script

## 1. Start the backend

```powershell
python -m uvicorn backend.app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## 2. Create a proposal

Use `POST /v1/proposals`:

```json
{
  "inquiry": "Looking for a 2 bedroom investment on Yas Island under AED 1.8M with good ROI",
  "require_approval": true
}
```

Show:

- structured lead extraction
- CRM-ready lead qualification score
- ranked recommendations from 109 connected listings
- AVM-style yield and risk calculations
- mortgage affordability estimates
- area rationale
- pending approval status

## 3. Approve the run

Use `POST /v1/runs/{run_id}/approval`:

```json
{
  "approved": true,
  "reviewer": "Demo Agent",
  "note": "Approved after reviewing budget fit, area match, and ROI."
}
```

Open the returned `pdf_url`.

## Interview positioning

"This compresses a 45-90 minute broker workflow into an auditable, human-governed agent pipeline."
