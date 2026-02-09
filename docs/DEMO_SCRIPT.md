# DealSense AI -- Demo Script

**Scenario:** Ravi Kiran (Account Executive, DXC Luxoft) is preparing for, conducting, and closing out a discovery call with ANZ Bank's Trade Finance team.

**Deal:** ANZ Bank -- Trade Finance Platform Modernization ($4.5M)

---

## Act 1: Before the Call (Pre-Call Preparation)

**Setup:** Ravi opens DealSense AI in his browser and selects the *ANZ Bank -- Trade Finance* deal from the sidebar.

### 1.1 Deal Context Loads Automatically

The **Context Panel** (right sidebar) populates with:

| Section            | What the Seller Sees                                                                 |
|--------------------|--------------------------------------------------------------------------------------|
| Call Details       | Customer: ANZ Bank, Contact: David Chen (Head of Trade Operations), Stage: Discovery |
| Similar Deals (3)  | CBA -- Trade Finance Platform ($5.2M, Won), SMBC -- LC Automation ($3.8M, Won), SCB -- Trade Digitization ($4.1M, In Progress) |
| Credible References| Andrew Marvin (ASX/ex-CBA, Head of Derivatives Clearing), Ian Stephenson (Standard Chartered, CIO Trade & Working Capital) -- both linked to LinkedIn |
| Expected Questions | *Team & Delivery:* "CBA team size?", "Timeline?" / *Data Privacy:* "SCB privacy approach?" / *AI Capabilities:* "AI in production?", "Accuracy?" |
| Talking Points     | "CBA: 45-person team, 18-month timeline", "SMBC: Integrated 3 core systems + SWIFT", "SCB: Singapore-only for data privacy", "AI POC: 92% doc classification accuracy" |

### 1.2 Seller Clicks "Prepare for upcoming call"

Ravi clicks the **Prepare** action chip. The AI assistant responds in the chat panel with a structured briefing:

> **ANZ Bank -- Discovery Call Briefing**
>
> ANZ processes ~5,000 letters of credit per month. Key pain points from prior conversations include manual document classification, slow compliance checks, and fragmented integration with core banking.
>
> **Recommended approach:** Lead with the CBA case study (45-person team, 92% AI classification accuracy). ANZ's David Chen will likely ask about team sizing, timeline, and data sovereignty -- use the SCB Singapore model as a privacy reference.
>
> **References to drop:** Andrew Marvin can speak to CBA clearing integration; Ian Stephenson can validate our trade finance platform at Standard Chartered.

### 1.3 Seller Clicks "Expected Questions"

The AI returns a prioritized list of likely questions with suggested answers sourced from the RAG knowledge base.

**Demo talking point:** "All of this context was pulled automatically from ingested MoMs, case studies, and reference profiles -- zero manual prep."

---

## Act 2: During the Call (Live Assistance)

**Setup:** Ravi clicks **Start Live Call**. The **LiveCallStrip** appears at the top of the screen showing a red "LIVE" badge, call duration timer, and connection status.

### 2.1 Live Transcription

As the call progresses, transcript chunks stream into the system in real time via WebSocket. The connection status cycles through: *Connecting > Connected > Transcribing*.

### 2.2 Real-Time RAG Query (Push-to-Talk)

Mid-call, David Chen asks: *"How large was the team on the CBA implementation?"*

Ravi presses **Shift+Space** (push-to-talk hotkey) and types into the chat:

> "What was CBA team size?"

The AI responds instantly:

> **45 members** -- a cross-functional team including 12 DXC engineers, 18 CBA business analysts, and 15 integration specialists. The engagement ran 18 months across 3 phases.
>
> *Source: CBA Trade Finance Platform case study, Q3 2025*

### 2.3 Handling an Objection

David raises a concern: *"We're worried about data leaving Australia."*

Ravi clicks the **Handle objection** action chip and types the concern. The AI responds:

> All data processing occurs within Azure Australia East (Sydney). Our SCB engagement used a Singapore-only deployment with identical architecture. We can provide a data residency guarantee in the SOW. Reference: Ian Stephenson at Standard Chartered can confirm the approach.

**Demo talking point:** "The seller never left the call interface. Sub-5-second answers, grounded in your own deal history -- not generic internet search."

---

## Act 3: After the Call (Post-Call Automation)

**Setup:** Ravi clicks **End Call** on the LiveCallStrip. The system transitions to the After Call phase.

### 3.1 Automatic Summary Generation

A loading spinner appears: *"Generating call summary... This may take 30-60 seconds"*

The **CallSummaryPanel** then renders with:

#### Deal Health Score: 7/10

> "Positive engagement from ANZ Trade Operations team. David Chen confirmed budget allocation and expressed strong interest in the CBA reference. Next step confirmed: technical deep-dive with ANZ's architecture team. Risk: no direct executive sponsor identified yet."

#### Executive Summary

> Discovery call with ANZ Bank's Trade Finance team covered platform modernization requirements, including LC processing automation for 5,000 monthly transactions. ANZ confirmed FY26 budget allocation. DXC Luxoft's CBA case study resonated strongly. Next step: technical architecture session scheduled for Feb 18.

#### Key Discussion Points (6)

1. ANZ processes 5,000 LCs/month with 40% manual handling
2. Current platform is 15 years old, approaching end-of-life
3. Compliance team spending 3 hours per LC on document review
4. ANZ open to phased rollout starting with document classification
5. Budget confirmed: $4-5M over 18 months
6. Integration with ANZ's core banking system (Temenos) is a hard requirement

#### Customer Pain Points

| Pain Point                    | Severity | Context                                    |
|-------------------------------|----------|--------------------------------------------|
| Manual document classification| High     | 40% of LCs require manual review           |
| Slow compliance checks        | High     | 3 hours per LC, regulatory pressure growing |
| Fragmented system integration | Medium   | 4 disconnected platforms                   |

#### Objections Raised

| Objection            | Category  | Suggested Response                               |
|----------------------|-----------|--------------------------------------------------|
| Data sovereignty     | Technical | Azure Australia East; reference SCB Singapore model |
| 18-month timeline    | Delivery  | Propose 3-phase approach; Phase 1 value in 4 months |

### 3.2 Action Items Extracted (5)

| # | Task                                                  | Owner  | Due Date   | Priority |
|---|-------------------------------------------------------|--------|------------|----------|
| 1 | Send CBA case study (sanitized) to David Chen         | Seller | 2026-02-11 | High     |
| 2 | Schedule technical deep-dive with ANZ architecture team| Seller | 2026-02-14 | High     |
| 3 | Prepare data residency guarantee language for SOW     | Seller | 2026-02-18 | Medium   |
| 4 | Connect Andrew Marvin with David Chen for CBA reference call | Seller | 2026-02-21 | Medium |
| 5 | ANZ to share current Temenos integration documentation | Customer | 2026-02-18 | High   |

### 3.3 Seller Approves and Writes Back to SharePoint

Ravi reviews the summary and action items, checks boxes for accuracy, and clicks **Approve**. The MoM is written back to the designated SharePoint folder via Microsoft Graph API.

**Demo talking point:** "From call end to a complete, PII-scrubbed MoM with prioritized action items in SharePoint -- under 2 minutes. That used to take 45 minutes of manual work."

---

## Key Metrics to Highlight During Demo

| Metric                  | Before DealSense | With DealSense | Improvement        |
|-------------------------|------------------|----------------|--------------------|
| Call prep time          | 30-45 min        | 2 min          | ~90% reduction     |
| MoM creation time       | 30-45 min        | < 2 min        | ~95% reduction     |
| Follow-up action items  | Often missed     | 100% captured  | Systematic capture |
| RAG query response time | N/A              | < 5 seconds    | Real-time          |
| Reference suggestions   | Manual recall    | Automatic      | Always available   |

---

## Demo Environment Checklist

- [ ] Backend running: `python backend/api.py` (FastAPI on `localhost:8000`)
- [ ] Frontend running: `cd ui/seller_panel && npm run dev` (Vite on `localhost:5173`)
- [ ] Vector store loaded with reference profiles and case studies
- [ ] Sample deal "ANZ Bank -- Trade Finance" pre-configured
- [ ] Microphone permissions enabled (for live call demo)
- [ ] Stable internet connection (for Azure OpenAI calls)

---

## Troubleshooting

| Issue                          | Fix                                                          |
|--------------------------------|--------------------------------------------------------------|
| Context panel shows mock data  | Ensure backend is running and `/api/deals/{id}/context` returns real data |
| Live call not connecting       | Check WebSocket connection and microphone permissions        |
| Summary generation fails       | Verify `AZURE_OPENAI_API_KEY` is set in `.env`              |
| SharePoint write-back fails    | Confirm Microsoft Graph API credentials and SharePoint site ID |
