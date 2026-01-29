# DealSense AI - Sales Assist Agent

An AI-powered sales assistant that leverages meeting notes (MoMs) to provide intelligent insights and automate post-call documentation.

## Architecture Overview

| Flow Step          | Azure Service                      | Purpose                     |
| ------------------ | ---------------------------------- | --------------------------- |
| SharePoint input   | Microsoft Graph API                | Native, secure access       |
| Ingestion job      | Azure Function (Timer Trigger)     | Serverless ingestion        |
| Raw doc storage    | Azure Blob Storage                 | Store original text         |
| Sanitization (PII) | Azure Container App (SLM)          | Runs inside VNet            |
| Chunking           | Same Container App                 | Text processing             |
| Embeddings         | Azure OpenAI (Embeddings)          | Enterprise-safe             |
| Vector DB          | Azure AI Search (vector)           | Managed vector search       |
| Retrieval (RAG)    | Azure Function / API App           | Stateless logic             |
| Reasoning LLM      | Azure OpenAI (GPT-4.x)             | Enterprise controls         |
| UI                 | Static Web App / Teams tab         | Fast MVP                    |
| Write-back         | Graph API -> SharePoint            | Source of truth             |

## Project Structure

```
dealsense-ai/
├── ingestion/           # Data ingestion pipeline
│   ├── sharepoint_connector/   # Microsoft Graph API integration
│   ├── sanitization/           # PII redaction
│   └── chunking/               # Document chunking
├── rag/                 # Retrieval-Augmented Generation
│   ├── embeddings/             # Embedding generation
│   ├── retrieval/              # Vector search logic
│   └── prompts/                # Prompt templates
├── post_call/           # Post-call automation
│   ├── mom_generator/          # Meeting notes generation
│   └── sharepoint_writer/      # Write-back to SharePoint
├── ui/                  # User interface
│   └── seller_panel/           # Seller approval panel
├── infra/               # Infrastructure as Code
│   ├── terraform/              # Terraform configurations
│   └── env/                    # Environment configs
├── tests/               # Test suites
└── docs/                # Documentation
```

## Team Responsibilities

| Person | Focus Area | Components |
|--------|------------|------------|
| Person 1 | Data / Backend | SharePoint connector, Ingestion job, Chunking + embeddings, Vector DB setup |
| Person 2 | AI / RAG | Prompt design, Retrieval logic, LLM integration, Output formatting |
| Person 3 | UI / Integration | Simple UI or Teams panel, Seller approval flow, Write-back to SharePoint |

## Branching Strategy

| Branch      | Who         | Purpose             |
| ----------- | ----------- | ------------------- |
| `main`      | CI/CD only  | Stable, deployable  |
| `dev`       | All devs    | Integration testing |
| `feature/*` | Individuals | New features        |
| `fix/*`     | Individuals | Bug fixes           |

### Branch Naming Examples

- `feature/sharepoint-ingestion`
- `feature/vector-retrieval`
- `feature/mom-generation`
- `fix/pii-redaction-bug`

## Getting Started

```bash
# Clone the repository
git clone https://github.com/ravikiran10jan/dealsense-ai.git
cd dealsense-ai

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

## Prerequisites

- Python 3.10+
- Azure subscription
- Microsoft 365 tenant with SharePoint access
- Azure OpenAI access

## License

Proprietary - Internal Use Only
