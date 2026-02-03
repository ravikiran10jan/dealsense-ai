# DealSense AI - Copilot Instructions

## Project Summary
**DealSense AI** is an enterprise sales assistant leveraging RAG (Retrieval-Augmented Generation) to process meeting notes (MoMs) from SharePoint, generate insights, and automate post-call documentation. Three distinct workstreams: data pipeline, AI/RAG logic, and seller approval UI.

---

## Architecture & Data Flow

### Core Pipeline
```
SharePoint MoMs → Graph API → Ingestion → Sanitization + Chunking → 
Embeddings → Azure AI Search (vector) → LLM Retrieval → GPT-4 Reasoning → 
Seller UI Approval → Write-back to SharePoint
```

### Key Components
- **ingestion/**: Fetches documents via Microsoft Graph API, manages blob storage
  - `sharepoint_connector/`: OAuth integration with Microsoft Graph
  - `sanitization/`: PII redaction (regex-based, SLM-planned)
  - `chunking/`: Text splitting using tiktoken
- **rag/**: Core ML pipeline
  - `embeddings/`: Azure OpenAI `text-embedding-ada-002`
  - `retrieval/`: Vector search + semantic ranking via Azure AI Search
  - `prompts/`: System prompts and templates (GPT-4 context)
- **post_call/**: Output generation and write-back
  - `mom_generator/`: LLM-generated MoM synthesis
  - `sharepoint_writer/`: Graph API write-back
- **ui/seller_panel**: React 18 + Vite frontend (Before/During/After tabs)

### Technology Stack
- **Backend**: Python 3.10+, FastAPI, Azure services
- **Frontend**: React 18, Vite, CSS Modules
- **AI/Search**: Azure OpenAI (embeddings, GPT-4), Azure AI Search (vector DB)
- **Auth**: Microsoft Graph API with OAuth 2.0
- **Infrastructure**: Azure (Container Apps, Functions, Blob, Static Web App), Terraform

---

## Critical Developer Workflows

### Python Backend Setup
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### UI Development (Node.js)
```bash
cd ui/seller_panel
npm install
npm run dev    # Start dev server (Vite + Express)
npm run build  # Production build
```

### Testing
- **Python**: `pytest` with `pytest-asyncio` for async Azure SDK calls
- **Code Quality**: `black` (formatter), `ruff` (linter), `mypy` (type checker)

### Environment Configuration
- Copy `.env.example` to `.env` in project root
- Required keys: `AZURE_*` credentials, `OPENAI_API_KEY`, `SHAREPOINT_*`

---

## Project-Specific Conventions

### Python Module Structure
- **Async-first**: All Azure SDK calls use `async/await` (e.g., `AzureOpenAI`, blob client)
- **Error handling**: Wrap Microsoft Graph and Azure SDK calls in try-catch; log context
- **Imports**: Organize as `azure.*` → `langchain` → local modules
- **Type hints**: Use `Pydantic` models for all API contracts (see `requirements.txt`)

### React Component Patterns
- **CSS Modules**: Every component has a `.module.css` file (e.g., `BeforeCall.jsx` + `BeforeCall.module.css`)
- **File structure**: Components organized by workflow (BeforeCall, DuringCall, AfterCall, Header, Navigation)
- **JSDoc comments**: Include LAYOUT diagrams for container components (see `App.jsx`)
- **Mock data**: `src/data/mockData.js` contains shared deal objects for UI testing
- **CSS variables**: Global theme in `src/styles/globals.css` (colors, spacing, typography)

### Git Branching
- `main` ← CI/CD only (stable)
- `dev` ← integration testing (all devs merge here)
- `feature/*` → Individual features (e.g., `feature/sharepoint-ingestion`)
- `fix/*` → Bug fixes (e.g., `fix/pii-redaction-bug`)

---

## Integration Points & Dependencies

### Microsoft Graph API (ingestion/sharepoint_connector)
- Authenticates as service principal; reads MoM files from SharePoint library
- Rate limits: 2000 requests/60s; batch requests when fetching multiple docs
- Response paging handled automatically by SDK

### Azure OpenAI (rag/embeddings, prompts)
- **Embeddings**: `text-embedding-ada-002`, 1536 dimensions, used for chunked documents
- **LLM**: GPT-4 (not 3.5); system prompt in `rag/prompts/` defines tone, format constraints
- **Cost**: Embeddings are cheap; LLM calls (reasoning) are expensive—batch intelligently

### Azure AI Search (rag/retrieval)
- **Hybrid mode**: Combines BM25 (keyword) + vector search; **default: vector-only** unless ADR changes
- **Index schema**: Fields = `id`, `content`, `chunk_index`, `embedding` (1536-dim vector)
- **Query pattern**: Retrieve top-k chunks, rerank, then pass to LLM

### PII Sanitization (ingestion/sanitization)
- **Current**: Regex patterns (email, SSN, credit card)
- **Planned**: Small Language Model (SLM) in Container App for context-aware redaction
- **Decision**: Runs inside VNet before any LLM exposure

---

## When Modifying Key Files

### Adding a New RAG Component
1. Create module in `rag/{component}/` with `__init__.py`
2. Use `Pydantic` for input/output contracts
3. Async functions for Azure SDK calls
4. Document assumptions in docstrings (chunk size, embedding dims, etc.)

### Updating Prompts
- Edit `rag/prompts/*.md` or `*.py` files
- Test with real embeddings (not mock)—context length matters for GPT-4
- Version prompts in comments (e.g., `# v2.1: Added instruction for tone`)

### Adding UI Tabs
1. Create component in `ui/seller_panel/src/components/{TabName}/`
2. Add `.module.css` with responsive classes
3. Import in `App.jsx` and add to `renderTabContent()` switch
4. Use `mockData.js` for development

### Infrastructure Changes
- Edit `infra/terraform/*.tf`
- Follow Azure naming conventions (e.g., `<project>-<service>-<env>`)
- Test locally if possible (Azure Bicep emulator); validate with `terraform plan`

---

## Common Pitfalls to Avoid

- **Embedding dimension mismatch**: If using newer embedding model, update search index schema (1536 → 3072)
- **PII leakage**: Always sanitize *before* chunking, never skip this step
- **Rate limiting**: Graph API and OpenAI have quotas; add exponential backoff retry logic
- **State management in UI**: BeforeCall, DuringCall, AfterCall are separate tab contexts—use top-level App state or localStorage for persistence
- **Async/await in Python**: Don't mix sync/async; use `asyncio.run()` only in entry points

---

## Key Files Reference

| File | Purpose |
|------|---------|
| [docs/architecture.md](docs/architecture.md) | System diagram and data flow |
| [docs/decisions.md](docs/decisions.md) | ADRs: vector DB, PII approach, embedding model |
| [ui/seller_panel/src/App.jsx](ui/seller_panel/src/App.jsx) | Tab navigation orchestrator; entry point |
| [rag/prompts/](rag/prompts/) | LLM system prompts and templates |
| [ingestion/sanitization/](ingestion/sanitization/) | PII redaction logic |
| [infra/terraform/main.tf](infra/terraform/main.tf) | Azure resource definitions |
