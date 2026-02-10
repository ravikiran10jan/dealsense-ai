# Architecture Decision Records (ADRs)

## ADR-001: Vector Database Selection

**Status**: Accepted

**Context**: Need a vector database for storing and retrieving document embeddings.

**Decision**: Use Azure AI Search with vector capabilities.

**Rationale**:
- Native Azure integration
- Managed service (no operational overhead)
- Supports hybrid search (vector + keyword)
- Enterprise-ready with RBAC and VNet support

---

## ADR-002: PII Sanitization Approach

**Status**: Proposed

**Context**: Meeting notes may contain sensitive information that should not be sent to LLMs.

**Decision**: Use regex-based sanitization initially, with SLM-based approach planned.

**Rationale**:
- Regex provides immediate baseline protection
- SLM can be added later for context-aware redaction
- Runs in Container App within VNet for security

---

## ADR-003: Embedding Model

**Status**: Accepted

**Context**: Need to generate embeddings for document chunks.

**Decision**: Use Azure OpenAI text-embedding-ada-002 (or newer).

**Rationale**:
- Enterprise data handling guarantees
- High quality embeddings
- Consistent with Azure-first approach
