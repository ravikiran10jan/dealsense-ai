# Responsible AI -- DealSense AI

This document describes how DealSense AI addresses responsible AI concerns across five pillars: PII protection, hallucination control, human-in-the-loop oversight, auditability, and transparency.

---

## 1. PII Protection

DealSense AI enforces a **"PII never reaches the LLM"** policy through a multi-layer sanitization pipeline that runs inside the Azure Container App before any text is sent to Azure OpenAI.

### Tokenization at Ingestion

| Step | Component | What happens |
|------|-----------|--------------|
| Detect | `backend/privacy/pii_detector.py` | Regex-based detection of **EMAIL, PHONE, SSN, CREDIT_CARD, IP_ADDRESS**. Includes Luhn validation for credit cards and false-positive filtering (dates, overlapping matches). |
| Tokenize | `backend/privacy/tokenizer.py` | Each PII span is replaced with a reversible token (`[PII:EMAIL:abc123def]`). The original value is **AES-encrypted** and stored in a local SQLite database (`pii_mappings.db`) keyed by `token_id`. |
| Orchestrate | `backend/privacy/sanitizer.py` | `Sanitizer.sanitize()` chains detection and tokenization in a single call, returning sanitized text plus token IDs. A post-sanitization `validate_sanitization()` check confirms no raw PII remains. |

Sanitization is invoked during deal ingestion (`api.py` -- `ingest_deal_to_vector_store()`) so that only tokenized text is embedded and indexed in the vector store.

### Detokenization Controls

- Detokenization (`Sanitizer.desanitize()`) is restricted to **admin-role** users via RBAC checks in `backend/privacy/auth.py`.
- Every detokenization call is audit-logged with `pii_accessed = true` (see Section 4).
- The tokenizer tracks `accessed_count` and `last_accessed` per token for compliance reporting.

### Data Residency

- PII mappings remain in the Container App's encrypted SQLite store; they are **never sent** to Azure OpenAI or Azure AI Search.
- All services run within an Azure VNet where applicable (see `docs/architecture.md`).

---

## 2. Hallucination Control

### RAG-First Retrieval with Source Citation

The hybrid answer pipeline in [`backend/orchestration/hybrid_answer.py`](../backend/orchestration/hybrid_answer.py) enforces a strict retrieval hierarchy:

1. **Vector DB search** -- FAISS semantic search retrieves `k=5` (general queries) or `k=3` (live-call queries) candidate chunks with L2 distance scores.
2. **Similarity threshold gate** -- Only results with `best_score < 1.8` (L2 distance) are considered relevant. Scores above 1.8 are treated as irrelevant and the pipeline moves to the next fallback.
3. **Web search fallback** -- If RAG results are not relevant, a web search provides grounding context.
4. **LLM knowledge fallback** -- Used only when both RAG and web search fail. The response is explicitly tagged as `source_type: "LLM"`.

Every response object includes:

```json
{
  "answer": "...",
  "sources": ["deal_xyz.pdf", "..."],
  "source_type": "RAG" | "WEB" | "LLM" | "RAG+CALL",
  "confidence": 0.85
}
```

### Confidence Scoring

For live-call queries, a confidence score is computed from the L2 distance:

```
confidence = max(0.5, min(1.0, 1.0 - (best_score / 2)))
```

Low-confidence answers signal the UI to surface caveats to the seller.

### Deterministic LLM Settings

| Use case | Temperature | Rationale |
|----------|-------------|-----------|
| General Q&A (`answer_llm.py`) | **0** | Maximizes factual consistency |
| Talking points (`talking_points.py`) | **0.3** | Allows minor creative variation while staying grounded in RAG context |
| Call summaries (`call_summary.py`) | **0** | Deterministic extraction of action items and deal health |

### Prompt-Level Grounding

The answer LLM system prompt (`answer_llm.py`) explicitly instructs the model to:

1. Check whether the provided context contains relevant information.
2. **Cite the context** when using it.
3. Fall back to general knowledge only when context is not relevant.

---

## 3. Human-in-the-Loop

### Seller Approval Flow

The seller panel UI (`ui/seller_panel/`) implements a **three-phase approval workflow** that keeps a human in the loop at every stage of a deal interaction:

| Phase | UI Tab | Seller Actions |
|-------|--------|----------------|
| **Before Call** | `BeforeCall.jsx` | Review deal context, similar deals, credible references, and suggested talking points. Download a pre-call summary PDF. |
| **During Call** | `DuringCall.jsx` | Take live notes, view real-time deal references, flag deal breakers, use push-to-talk for RAG-assisted queries. |
| **After Call** | `AfterCall.jsx` | Document highlights, risks, deal outcome (Won/Lost/Follow-up), client feedback score (1-10), and next steps. **Generate Final Report** only after seller review. |

### Confirmation Gates

- **MoM generation** requires the seller to click "Generate Final Report" after reviewing and editing the call summary -- the system does not auto-publish.
- **SharePoint write-back** occurs only after the seller approves the final report through the UI.
- All form submissions display save-confirmation messages before persisting data.
- CRM field updates (deal stage, next steps) require explicit seller input in the After Call form.

### No Autonomous Actions

DealSense AI does **not** autonomously send emails, update CRM records, or write back to SharePoint. Every external action requires a seller-initiated confirmation in the UI.

---

## 4. Auditability

### Comprehensive Audit Logger

The audit system ([`backend/privacy/audit_logger.py`](../backend/privacy/audit_logger.py)) records every significant operation with the following fields:

| Field | Description |
|-------|-------------|
| `timestamp` | UTC ISO-8601 timestamp |
| `user_id` | Authenticated user identifier |
| `user_role` | RBAC role (admin, user) |
| `action` | Action type (see table below) |
| `resource_type` | deal, transcript, rag, pii, call |
| `resource_id` | Specific resource identifier |
| `ip_address` | Client IP |
| `user_agent` | Client user agent |
| `status` | success, failure, denied |
| `pii_accessed` | Boolean flag for PII reveal events |
| `metadata` | JSON with **hashed** sensitive fields |

### Tracked Action Types

| Category | Actions |
|----------|---------|
| API | `api_request` |
| RAG | `query`, `search` |
| Deals | `deal_create`, `deal_read`, `deal_update`, `deal_delete` |
| PII | `pii_sanitize`, `pii_detokenize`, `pii_delete` |
| Auth | `auth_success`, `auth_failure`, `key_create`, `key_revoke` |

### PII-Safe Logging

To prevent PII leakage through logs, the audit logger applies `_sanitize_metadata()`:

- Fields named `query`, `content`, `notes`, `text`, or `message` are **SHA-256 hashed** before storage -- the plaintext is never written to the audit database.
- Nested dictionaries are recursively sanitized.

### Admin Query Interface

- `GET /api/privacy/audit` -- Filter logs by user, action, resource, date range, or PII-only events (admin only).
- `GET /api/privacy/stats` -- Aggregate statistics: total events, unique users, PII access count, failed auth attempts, events by action type.

---

## 5. Transparency

### Source Attribution in the UI

Every RAG-powered answer returned to the seller includes a `source_type` field that the UI can render as a provenance badge:

| Badge | Meaning |
|-------|---------|
| **RAG** | Answer grounded in indexed deal knowledge base |
| **RAG+CALL** | Answer grounded in knowledge base + live call transcript |
| **WEB** | Answer grounded in real-time web search results |
| **LLM** | Answer generated from model knowledge only (no retrieval grounding) |

The `sources` array lists the specific documents or search results used, and the `confidence` score (0.5 -- 1.0) provides a numeric reliability indicator.

### Credible References

When the system surfaces reference contacts (`backend/llm/credible_references.py`), each reference is retrieved from the knowledge base with full metadata (name, company, role, relationship, LinkedIn URL) -- not hallucinated by the model.

### Threshold Visibility

Key configuration values that affect answer quality are documented and tunable:

| Parameter | Value | Location |
|-----------|-------|----------|
| Similarity threshold | `1.8` (L2) | `hybrid_answer.py:9` |
| RAG retrieval count | `k=5` (general), `k=3` (live call) | `hybrid_answer.py:23,101` |
| LLM temperature | `0` -- `0.3` | `answer_llm.py`, `talking_points.py`, `call_summary.py` |
| Transcript limit | 15,000 chars | `call_summary.py:70` |

---

## Known Gaps and Roadmap

The following areas are acknowledged as incomplete and tracked for future work:

| Gap | Description |
|-----|-------------|
| **Bias monitoring** | No automated fairness metrics for deal scoring across industries, company sizes, or geographies. |
| **Model drift detection** | No monitoring for embedding quality or LLM output degradation over time. |
| **Adversarial robustness** | No prompt-injection or jailbreak testing harness. |
| **Data retention policy** | No automated PII token expiration or GDPR right-to-erasure workflow beyond manual `pii_delete`. |
| **Consent tracking** | No explicit user consent recording for data processing. |
| **SLM-based PII detection** | Current regex-based detection is planned to be augmented with a small language model for context-aware redaction (see ADR-002 in `docs/decisions.md`). |
