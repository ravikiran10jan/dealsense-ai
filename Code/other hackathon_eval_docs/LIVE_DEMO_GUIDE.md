# DealSense AI -- Live Demo Guide

| Service | URL |
|---------|-----|
| **Frontend** | [https://dealsense-ai-frontend.onrender.com](https://dealsense-ai-frontend.onrender.com/) |
| **API Backend** | [https://dealsense-ai-api.onrender.com](https://dealsense-ai-api.onrender.com/) |

This guide walks you through testing DealSense AI on the live deployment. The app is pre-loaded with Trade Finance deals for Financial Services & Banking clients.

---

## Quick Start

1. Open [https://dealsense-ai-frontend.onrender.com](https://dealsense-ai-frontend.onrender.com/) in your browser (Chrome or Edge recommended)
2. The app loads with **Apex National Bank -- Trade Finance** pre-selected
3. Follow the three-act walkthrough below

> **Note:** The first load may take 30-60 seconds if the Render instance is cold-starting. Refresh if you see a blank page on initial load.

---

## What You Will See

The UI is a three-panel layout:

| Panel | Position | Purpose |
|-------|----------|---------|
| **Sidebar** | Left | Deal list, navigation (Inbox, My Calls), add new deals |
| **Chat Panel** | Center | AI assistant chat, action chips, transcript (during live calls) |
| **Context Panel** | Right | Deal details, similar deals, references, questions, talking points |

---

## Act 1: Before Call -- Explore Pre-Call Preparation

### Step 1: Review the Deal Context (automatic)

When the app loads, the **Context Panel** on the right shows AI-curated context for the Apex National Bank deal:

- **Call Details** -- Customer: Apex National Bank, Contact: Mark Johnson (Head of Trade Finance Operations), Stage: Discovery, Deal: $4.5M
- **Similar Deals** -- 3 comparable deals: Pacific Trust Bank Trade Finance Platform ($5.2M, Won), Global Trade Bank LC Automation ($3.8M, Won), Eastern Commerce Bank Trade Digitization ($4.1M, In Progress)
- **Credible References** -- Robert Clarke (National Securities Exchange/ex-PTB) and Thomas Blake (Eastern Commerce Bank) with LinkedIn profile links
- **Expected Questions** -- Grouped by theme: Team & Delivery, Data Privacy, AI Capabilities
- **Suggested Talking Points** -- Key data points from prior deals (PTB team size, Global Trade Bank integrations, Eastern Commerce Bank privacy model, AI accuracy)

### Step 2: Use the AI Chat Assistant

Click the action chips at the bottom of the chat panel:

| Action Chip | What It Does |
|-------------|-------------|
| **Prepare for upcoming call** | AI generates a structured pre-call briefing with deal context, recommended approach, and references to mention |
| **Show similar customers** | AI retrieves and summarizes similar deals from the knowledge base |
| **Expected questions** | AI lists likely customer questions with suggested answers |
| **Draft discovery questions** | AI generates discovery questions tailored to the deal |

You can also type free-form questions in the chat input, such as:
- "What was the Pacific Trust Bank team size?"
- "Tell me about our trade finance capabilities"
- "What are the key risks for this deal?"

### Step 3: Switch Between Deals

Click other deals in the sidebar to see context change:

| Deal | Customer | Stage | Amount |
|------|----------|-------|--------|
| Apex National Bank | Mark Johnson | Discovery | $4.5M |
| Island Pacific Bank | Anna Lee | Proposal | $2.8M |
| Summit Financial Group | James Reed | Discovery | $3.6M |
| Meridian Bank | Rachel Grant | Discovery | $3.2M |

Each deal loads its own context panel with relevant similar deals, references, and talking points.

### Step 4: Add a New Deal

1. Click the **+ Add Deal** button at the bottom of the sidebar
2. Fill in the form: account name, stage, call date/time, deal amount, contact details, industry
3. Click **Create Deal** -- the new deal appears in the sidebar with auto-populated context

---

## Act 2: During Call -- Test Live Call Features

### Step 1: Start a Live Call

1. Select **Apex National Bank** from the sidebar
2. Click the **Start Live Call** button in the Context Panel
3. The **LiveCallStrip** appears at the top showing:
   - Red "LIVE" badge with pulse animation
   - Call duration counter
   - Connection status (Connecting --> Connected --> Transcribing)
   - Controls: Transcript toggle, Mute, End Call

> **Note:** Live transcription requires a connected backend with AssemblyAI credentials. On the demo deployment, the connection attempt will show the UI flow even if the backend is unavailable.

### Step 2: Ask Real-Time Questions

During an active call, the action chips change to During Call mode:

| Action Chip | What It Does |
|-------------|-------------|
| **Live answer help** | Submit a question for real-time RAG-sourced answer |
| **Product FAQs** | Quick access to product knowledge |
| **Pricing guidance** | Pricing context from similar deals |
| **Handle objection** | AI generates grounded objection responses |

Type a question like "What was Pacific Trust Bank team size?" -- the AI responds with sourced answers from the knowledge base.

### Step 3: Observe the Push-to-Talk Flow

The push-to-talk hotkey is **Shift+Space**. During a live call, this activates the microphone for voice input. On the demo, you can simulate this by typing questions in the chat input.

---

## Act 3: After Call -- Review Summary and Action Items

### Step 1: End the Call

Click **End Call** on the LiveCallStrip. The system transitions to the After Call phase:

1. A loading spinner appears: "Generating call summary..."
2. The **CallSummaryPanel** renders with:

### Step 2: Review the Call Summary

The summary includes:

- **Deal Health Score** (1-10) with color-coded badge (green >= 8, yellow >= 6, orange >= 4, red < 4)
- **Executive Summary** -- 2-3 sentence overview of the call
- **Key Discussion Points** -- Expandable list of main topics covered
- **Customer Pain Points** -- Cards with severity indicators (High/Medium/Low)
- **Objections Raised** -- Cards with category and suggested responses
- **Next Steps** -- Specific agreements from the call

### Step 3: Review Action Items

The action items section shows:

- Task description
- Owner (Seller or Customer)
- Due date
- Priority badge (High = red, Medium = yellow, Low = green)
- Checkbox to mark complete

### Step 4: Post-Call Action Chips

The After Call action chips provide additional tools:

| Action Chip | What It Does |
|-------------|-------------|
| **Summarize this call** | Regenerate or refine the call summary |
| **Draft follow-up email** | AI drafts a follow-up email based on the call |
| **Update Salesforce** | Prepare CRM field updates |
| **Create action items** | Extract additional action items |

---

## Additional Features to Explore

### My Calls View

Click **My Calls** in the sidebar navigation to see:
- Upcoming scheduled calls with deal context
- Completed calls with duration and notes
- Click "Prepare" on any upcoming call to jump to pre-call mode

### Architecture Diagram

Click the **Architecture** button in the bottom-right corner to view the system architecture diagram showing the full Azure-native pipeline.

### Context Panel Toggle

Click the context panel toggle button (top-right of the chat panel) to show/hide the right sidebar for a wider chat view.

---

## What to Look For (Evaluator Notes)

### Agentic AI Behaviors
- **Pre-Call Prep Agent**: Notice how selecting a deal automatically triggers context retrieval (similar deals, references, questions, talking points) without manual search
- **Follow-Up Agent**: After ending a call, the system autonomously generates a structured MoM, extracts action items, and scores deal health
- **Risk Detection**: The system identifies deal risks from transcript analysis (competitor mentions, stalling signals, stakeholder gaps)

### RAG Pipeline Quality
- Ask factual questions like "What was Pacific Trust Bank team size?" or "Tell me about Eastern Commerce Bank's privacy approach" -- answers should be grounded in the knowledge base with source citations
- Note the `source_type` in responses: RAG (vector search), WEB (web search fallback), LLM (model knowledge only)

### Responsible AI
- **PII Protection**: All ingested data goes through PII detection and AES-encrypted tokenization before reaching the LLM
- **Human-in-the-Loop**: The seller must explicitly approve MoMs before SharePoint write-back -- no autonomous external actions
- **Transparency**: Every answer includes source attribution and confidence scoring
- See [docs/responsible_ai.md](responsible_ai.md) for the full Responsible AI framework

### UI/UX Design
- Brand colors (orange primary, dark navy sidebar, warm off-white background)
- Three-phase workflow (Before/During/After) with smooth transitions
- Responsive context panel with expandable sections
- Live call strip with real-time connection status

---

## Known Limitations

| Limitation | Context |
|-----------|---------|
| **Cold start delay** | Render Starter plan instances may sleep after inactivity; first load may take 30-60 seconds |
| **Live transcription** | Requires AssemblyAI credentials on the API backend; demo may show UI flow without live audio |
| **SharePoint write-back** | Requires Microsoft Graph API credentials; not active on demo deployment |
| **WebSocket** | Live call WebSocket depends on backend availability |

---

## Browser Support

| Browser | Status |
|---------|--------|
| Chrome 90+ | Fully supported |
| Edge 90+ | Fully supported |
| Firefox 90+ | Supported (WebSocket may vary) |
| Safari 15+ | Supported (microphone permissions may require extra step) |

---

## Related Documentation

- [HACKATHON.md](../HACKATHON.md) -- Hackathon submission overview
- [DEMO_SCRIPT.md](DEMO_SCRIPT.md) -- Detailed demo narrative for presenters
- [responsible_ai.md](responsible_ai.md) -- Responsible AI framework
- [architecture.md](architecture.md) -- System architecture
- [decisions.md](decisions.md) -- Architecture decision records
