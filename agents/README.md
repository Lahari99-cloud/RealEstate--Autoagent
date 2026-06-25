# Agent Design

The backend implements the interview demo as a LangGraph state machine with bounded agent responsibilities:

1. Buyer Agent / Lead Parser extracts budget, area, bedroom count, purpose, timeline, and language.
2. Lead Qualification Agent scores buyer intent, budget clarity, urgency, financing readiness, CRM stage, and next-best action.
3. Property Search Agent ranks the connected listing inventory from `data/psi_listings.json`.
4. Valuation Agent estimates market value, yield, cash flow, and risk flags.
5. Mortgage & Affordability Agent estimates down payment, loan amount, monthly payment, and income required.
6. Area Research Agent adds UAE community context and nearby landmarks.
7. Broker Handoff / Approval Gate pauses before client-facing output.
8. Proposal Writer renders the approved PDF proposal.

The trace returned by the API is intentionally safe: it exposes operational summaries, not hidden chain-of-thought.

The repository includes API and workflow tests as the foundation of an evaluation framework. Production-grade agent evaluation, including golden datasets, LLM-as-judge checks, regression tracking, latency metrics, and cost dashboards, is planned for the next iteration.
