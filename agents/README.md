# Agent Design

The backend implements the interview demo as a LangGraph state machine with bounded agent responsibilities:

1. Buyer Agent / Lead Parser extracts budget, area, bedroom count, purpose, timeline, and language.
2. Property Search Agent ranks the connected listing inventory from `data/psi_listings.json`.
3. Valuation Agent estimates market value, yield, cash flow, and risk flags.
4. Area Research Agent adds UAE community context and nearby landmarks.
5. Broker Handoff / Approval Gate pauses before client-facing output.
6. Proposal Writer renders the approved PDF proposal.

The trace returned by the API is intentionally safe: it exposes operational summaries, not hidden chain-of-thought.
