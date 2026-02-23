# DealSense AI -- Hackathon 2026 Submission

## Project Name

**DealSense AI** -- Agentic Sales Copilot for Enterprise B2B Sellers

## Live Demo

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | [https://dealsense-ai-frontend.onrender.com](https://dealsense-ai-frontend.onrender.com/) | Live |
| **API** | [https://dealsense-ai-api.onrender.com](https://dealsense-ai-api.onrender.com/) | Live |

See the [Live Demo Guide](docs/LIVE_DEMO_GUIDE.md) for a step-by-step walkthrough.

## Team

| Name | Role | Focus |
|------|------|-------|
| Alex Morgan | Lead Developer | Full-stack: backend API, agentic AI, RAG pipeline, frontend, deployment |

## Problem Statement

Enterprise B2B sellers in the Financial Services & Banking vertical spend **1-2 hours per day** on post-call administrative tasks -- writing meeting notes (MoMs), updating CRM records, drafting follow-up emails, and tracking action items. This leads to:

- **Missed follow-ups and lost deals** -- critical action items slip through the cracks
- **Inconsistent deal documentation** -- MoM quality varies by rep, making handoffs unreliable
- **Leadership blind spots on deal health** -- managers lack timely, structured signals to intervene early

For an enterprise account executive managing 15-20 active deals across major banking clients, this admin overhead directly reduces selling time and deal velocity.

## Solution

DealSense AI is an **agentic AI-powered sales copilot** that assists sellers across the entire call lifecycle:

### Before the Call
- **Pre-Call Prep Agent** automatically retrieves similar deals won, credible references (with LinkedIn profiles), expected customer questions, and tailored talking points from the RAG knowledge base
- Seller walks into every call fully prepared in under 2 minutes instead of 30-45 minutes

### During the Call
- **Live AI Assistant** provides real-time, RAG-sourced answers to seller questions via push-to-talk (Shift+Space)
- Handles objections with grounded responses citing prior deal experience
- Live transcription via WebSocket + AssemblyAI

### After the Call
- **Follow-Up Orchestration Agent** generates a structured MoM with executive summary, key discussion points, customer pain points, objections, and prioritized action items
- **Risk Detection Agent** analyzes the transcript for deal risks (competitor mentions, stalling signals, champion absence)
- Seller reviews, approves, and writes the MoM back to SharePoint -- human-in-the-loop at every stage

## Architecture

```
SharePoint (MoMs, Case Studies, Reference Profiles)
       |
       v
  Microsoft Graph API --> Azure Function (Timer Trigger)
       |
       v
  Azure Blob Storage (Raw Documents)
       |
       v
  Azure Container App (PII Sanitization + Chunking)
       |
       v
  Azure OpenAI (Embeddings) --> FAISS / Azure AI Search (Vector DB)
       |
       v
  Hybrid RAG Pipeline (Semantic Search + Web Search + LLM Fallback)
       |
       v
  Agentic AI Layer (3 Autonomous Agents with 5-Phase Reasoning Loop)
       |
       v
  FastAPI Backend (REST + WebSocket)
       |
       v
  React Frontend (Render) --> Seller Approval --> SharePoint Write-Back
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, CSS Modules, Express (proxy server) |
| **Backend** | Python 3.10, FastAPI, Uvicorn, WebSocket |
| **AI/LLM** | Azure OpenAI (GPT-4o-mini), LangChain |
| **Embeddings** | Azure OpenAI text-embedding-ada-002, FAISS |
| **Transcription** | AssemblyAI (real-time WebSocket) |
| **RAG** | Hybrid pipeline: FAISS vector search + DuckDuckGo web search + LLM fallback |
| **Privacy** | Regex + Luhn PII detection, AES-encrypted tokenization, RBAC |
| **Observability** | Opik (LLM tracing), Agent trace logging, Audit logger (SQLite) |
| **Deployment** | Render (frontend + API backend) |
| **Source Control** | GitHub, Git Flow (main/dev/feature/fix branches) |

## Agentic AI Architecture

DealSense AI implements three autonomous agents, each following a **5-phase reasoning loop**:

```
PERCEPTION --> PLANNING --> TOOL EXECUTION --> REFLECTION --> ACTION
```

| Agent | Trigger | Tools Used | Output |
|-------|---------|-----------|--------|
| **Pre-Call Prep** | Seller opens a deal | RAG search, reference lookup, LLM (talking points, questions) | Consolidated pre-call brief with confidence score |
| **Risk Detection** | Call ends or transcript snippet received | Keyword scan (regex), LLM deep-analysis | Risk alerts with severity, evidence, recommendations |
| **Follow-Up Orchestration** | Seller ends a call | MoM generation, action-item extraction, MEDDPICC gap check, health scoring | Complete follow-up package: MoM, action items, deal health score |

Every agent response includes an `agent_trace` array with per-phase timing for full observability.

## Responsible AI

DealSense AI addresses responsible AI across five pillars:

| Pillar | Implementation |
|--------|---------------|
| **PII Protection** | Multi-layer: regex detection + Luhn validation --> AES-encrypted tokenization. PII never reaches the LLM. Detokenization restricted to admin role with audit logging. |
| **Hallucination Control** | RAG-first retrieval with similarity threshold gate (L2 < 1.8). Every response tagged with `source_type` (RAG/WEB/LLM) and confidence score. Temperature = 0 for factual tasks. |
| **Human-in-the-Loop** | Three-phase seller approval flow. No autonomous external actions -- MoM generation, SharePoint write-back, and CRM updates all require explicit seller confirmation. |
| **Auditability** | Every API call, PII access, and agent execution logged with user identity, timestamp, and SHA-256 hashed sensitive content. Admin query interface for compliance. |
| **Transparency** | Source attribution badges (RAG/WEB/LLM) on every answer. Credible references retrieved from knowledge base with full metadata, not hallucinated. Tunable threshold parameters documented. |

Full details: [docs/responsible_ai.md](docs/responsible_ai.md)

## Key Features Demonstrated

| # | Feature | Where to See It |
|---|---------|----------------|
| 1 | Pre-call AI briefing with similar deals and references | Select any deal --> Context Panel (right sidebar) |
| 2 | RAG-powered chat assistant | Click "Prepare for upcoming call" or type a question |
| 3 | Credible reference lookup with LinkedIn profiles | Context Panel --> "Credible References" section |
| 4 | Expected questions and talking points | Context Panel --> expandable sections |
| 5 | Live call with real-time transcription | Click "Start Live Call" |
| 6 | Push-to-talk RAG queries during call | Press Shift+Space during live call |
| 7 | Automated MoM generation with deal health score | End call --> CallSummaryPanel |
| 8 | Action item extraction with owners and deadlines | Post-call summary --> Action Items section |
| 9 | Deal risk detection | Post-call agent analysis |
| 10 | PII tokenization and privacy controls | Automatic during ingestion; admin-only detokenization |
| 11 | Agent trace observability | API responses include `agent_trace` array |
| 12 | Human-in-the-loop approval gates | Seller must approve before SharePoint write-back |

## Impact Metrics

| Metric | Before DealSense | With DealSense | Improvement |
|--------|------------------|----------------|-------------|
| Call prep time | 30-45 min | < 2 min | ~90% reduction |
| MoM creation time | 30-45 min | < 2 min | ~95% reduction |
| Seller admin time per week | 8-10 hrs | 2-3 hrs | 60-70% reduction |
| Follow-up completion rate | ~60% | ~85% | 40% improvement |
| Deal velocity (opportunity to close) | Baseline | 10-15% faster | Measured by CRM data |
| RAG query response time | N/A | < 5 seconds | Real-time |

## Product Screenshots

### Before Call -- Pre-Call Preparation
![Before Call Panel](docs/screenshots/before-call-panel.png)

### During Call -- Live AI Assistant
![During Call Assistant](docs/screenshots/during-call-assistant.png)

### After Call -- Automated Summary & Action Items
![After Call Summary](docs/screenshots/after-call-summary.png)

## Target Market

Enterprise account executives at Financial Services and Banking clients managing complex, multi-stakeholder trade finance deals.

## How to Run Locally

```bash
# Backend
git clone https://www.linkedin.com/in/example-profile/dealsense-ai.git
cd dealsense-ai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure Azure OpenAI credentials
python backend/scripts/ingest_references.py
python backend/api.py  # Runs on http://localhost:8000

# Frontend (separate terminal)
cd ui/seller_panel
npm install && npm run build && npm run start  # Runs on http://localhost:3000
```

## Repository Structure

```
dealsense-ai/
├── backend/
│   ├── agents/           # 3 autonomous agents (5-phase reasoning loop)
│   ├── orchestration/    # Hybrid RAG pipeline
│   ├── retrieval/        # FAISS vector search
│   ├── llm/              # LLM integration (talking points, references, answers)
│   ├── summarization/    # Call summary + action item extraction
│   ├── privacy/          # PII detection, tokenization, RBAC, audit logging
│   ├── websocket/        # Live call WebSocket handling
│   └── api.py            # FastAPI endpoints
├── ui/seller_panel/      # React seller dashboard
├── docs/                 # Architecture, decisions, responsible AI, demo script
└── tests/                # Test suites
```

## Links

- **Live Demo (Frontend):** [https://dealsense-ai-frontend.onrender.com](https://dealsense-ai-frontend.onrender.com/)
- **Live Demo (API):** [https://dealsense-ai-api.onrender.com](https://dealsense-ai-api.onrender.com/)
- **GitHub:** [https://www.linkedin.com/in/example-profile/dealsense-ai](https://www.linkedin.com/in/example-profile/dealsense-ai)
- **Demo Script:** [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)
- **Live Demo Guide:** [docs/LIVE_DEMO_GUIDE.md](docs/LIVE_DEMO_GUIDE.md)
- **Responsible AI:** [docs/responsible_ai.md](docs/responsible_ai.md)
- **Architecture Decisions:** [docs/decisions.md](docs/decisions.md)
