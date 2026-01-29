# Architecture

## System Overview

DealSense AI is built on Azure services with a modular architecture supporting the RAG (Retrieval-Augmented Generation) pattern.

## Data Flow

```
SharePoint (MoMs)
       │
       ▼
┌──────────────────┐
│  Graph API       │ ◄── Timer-triggered Azure Function
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Blob Storage    │ ◄── Raw document storage
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Container App   │ ◄── PII sanitization + chunking
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Azure OpenAI    │ ◄── Embedding generation
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  AI Search       │ ◄── Vector storage & retrieval
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Azure OpenAI    │ ◄── LLM reasoning (GPT-4)
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Static Web App  │ ◄── Seller approval UI
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  SharePoint      │ ◄── Write-back approved MoMs
└──────────────────┘
```

## Security Considerations

- All services run within Azure VNet where applicable
- PII sanitization happens before any LLM processing
- Azure OpenAI provides enterprise-grade data handling
- Microsoft Graph API uses OAuth 2.0 authentication
