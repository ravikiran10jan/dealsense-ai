# DealSense AI - Full Stack Setup Guide

This guide covers the complete setup for DealSense AI, including the frontend UI, backend API, vector database, and LLM integration.

---

## Architecture Overview

```
Frontend (React) → Backend API (FastAPI) → Vector DB (FAISS) + LLM (OpenAI)
```

- **Frontend**: React 18 + Vite, runs on port 3000
- **Backend**: FastAPI + Uvicorn, runs on port 8000
- **Vector DB**: FAISS with TF-IDF embeddings (local)
- **LLM**: OpenAI GPT-4o-mini for RAG responses

---

## Prerequisites

| Component | Requirement |
|-----------|-------------|
| Node.js | v16+ (with npm 7+) |
| Python | 3.10+ |
| OpenAI API Key | Required for LLM features |
| Redis | Optional (for live call features) |

---

## Part 1: Backend Setup

### Step 1: Navigate to Project Root

```bash
cd dealsense-ai
```

### Step 2: Create Python Virtual Environment

```bash
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (web framework)
- LangChain (RAG orchestration)
- FAISS-CPU (vector database)
- OpenAI SDK (LLM integration)
- python-pptx (document processing)
- And other utilities

### Step 5: Configure Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file in the project root:

```env
# Required for LLM features
OPENAI_API_KEY=your-openai-api-key-here

# Azure Configuration (optional - for production)
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=
AZURE_OPENAI_CHAT_DEPLOYMENT=

# Azure AI Search (optional - for production)
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=
AZURE_SEARCH_INDEX_NAME=dealsense-vectors

# Application settings
LOG_LEVEL=INFO
ENVIRONMENT=development
```

Also create `backend/.env`:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
OPENAI_API_KEY=your-openai-api-key-here
```

### Step 6: Initialize Vector Database

The vector store must be created before using RAG features. Place your PPTX files in the data folders:

```
backend/
├── data/
│   ├── case_studies/    # Add .pptx case study files here
│   └── offerings/       # Add .pptx offering files here
```

Run ingestion to create the vector store:

```bash
cd backend
python main.py
```

This will:
1. Load PPTX files from `data/case_studies/` and `data/offerings/`
2. Chunk documents for retrieval
3. Create FAISS vector store at `backend/vector_store/dealsense_faiss/`

If the vector store already exists, it will skip ingestion and start the chat interface (press Ctrl+C to exit).

### Step 7: Generate API Key (Required for Authentication)

The backend API requires authentication. Generate an API key:

```bash
cd backend
python -m privacy.generate_api_key --user admin@example.com --role admin
```

**Available roles:**
- `admin` - Full access including PII and audit management
- `seller` - Create deals, query RAG, manage own deals
- `readonly` - Query RAG and view deals only

Save the generated API key - you'll need it for frontend configuration.

### Step 8: Start the Backend Server

```bash
cd backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

Verify it's running:
```bash
curl http://localhost:8000/api/health
# Should return: {"status": "healthy"}
```

---

## Part 2: Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd ui/seller_panel
```

### Step 2: Install Node.js Dependencies

```bash
npm install
```

This installs:
- React 18
- React DOM 18
- Express.js (Node server)
- Vite (Build tool)

### Step 3: Configure API Connection

The frontend connects to the backend at `http://localhost:8000`. If your backend runs on a different port, update the API base URL in the frontend code.

For API authentication, you'll need to include the API key in requests:
```javascript
headers: {
  'Content-Type': 'application/json',
  'X-API-Key': 'your-generated-api-key'
}
```

### Step 4: Build and Run Frontend

```bash
npm run build
npm run dev
```

The frontend will be available at: **http://localhost:3000**

---

## Part 3: Running the Full Stack

### Quick Start (Both Services)

**Terminal 1 - Backend:**
```bash
cd dealsense-ai
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
cd backend
uvicorn api:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd dealsense-ai/ui/seller_panel
npm run build && npm run dev
```

### Verify Integration

1. Open **http://localhost:3000** in your browser
2. The frontend should connect to the backend API
3. Try the search/query features - they should return RAG-powered responses

---

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/deals` | GET | Get mock deals |
| `/api/active-deals` | GET | Get active deals (auth required) |
| `/api/deals/create` | POST | Create new deal (auth required) |
| `/api/query` | POST | Query RAG system (auth required) |
| `/api/search` | GET | Semantic search (auth required) |
| `/api/talking-points` | POST | Generate talking points (auth required) |

All authenticated endpoints require the `X-API-Key` header.

---

## Optional: Redis Setup (Live Call Features)

For real-time call features, install and run Redis:

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis
```

**Windows:**
Use WSL2 or Docker:
```bash
docker run -d -p 6379:6379 redis
```

---

## Optional: Real Transcription

By default, transcription runs in mock mode. To enable real speech-to-text:

1. Sign up at [AssemblyAI](https://www.assemblyai.com/)
2. Add to `backend/.env`:
   ```env
   ASSEMBLYAI_API_KEY=your-assemblyai-key
   ```

---

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'xyz'"**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**"OPENAI_API_KEY not set"**
- Check `.env` file exists in both root and `backend/` directories
- Verify the API key is valid

**"Vector store not found"**
- Run `python main.py` in the `backend/` directory to create it
- Ensure PPTX files exist in `data/case_studies/` or `data/offerings/`

**"401 Unauthorized"**
- Generate an API key using `python -m privacy.generate_api_key`
- Include `X-API-Key` header in requests

### Frontend Issues

**"npm: command not found"**
- Install Node.js from https://nodejs.org/

**"Cannot connect to backend"**
- Verify backend is running on port 8000
- Check CORS settings if using different ports

**"Port 3000 already in use"**
- Kill the process using port 3000
- Or change the port in `server.js`

---

## Project Structure

```
dealsense-ai/
├── backend/
│   ├── api.py                 # FastAPI application
│   ├── main.py                # Ingestion & CLI
│   ├── ingestion/             # Document loaders & vector store
│   ├── retrieval/             # Semantic search
│   ├── llm/                   # LLM client & prompts
│   ├── orchestration/         # RAG orchestration
│   ├── privacy/               # Auth & PII handling
│   ├── data/                  # Source documents (PPTX)
│   └── vector_store/          # FAISS index (generated)
├── ui/
│   └── seller_panel/          # React frontend
│       ├── src/
│       ├── server.js
│       └── package.json
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── SETUP.md                   # This file
```

---

## Next Steps

1. Add your PPTX case studies to `backend/data/case_studies/`
2. Add your PPTX offerings to `backend/data/offerings/`
3. Re-run ingestion to update the vector store
4. Explore the API at http://localhost:8000/docs (Swagger UI)

---

**Questions?** Check the main README.md or reach out to the development team.
