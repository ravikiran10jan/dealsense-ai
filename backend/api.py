"""
FastAPI backend for DealSense AI
Integrates RAG search with the UI
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# Import RAG components
from orchestration.hybrid_answer import answer_query
from retrieval.semantic_search import semantic_search, load_vector_store

app = FastAPI(title="DealSense AI API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Deal(BaseModel):
    id: int
    title: str
    summary: str
    solutionArea: str
    industry: str
    benchmark: str
    caseStudy: str
    teamSize: str
    keyHighlights: List[str]
    dealBreakers: List[str]
    dealValue: str
    duration: str

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

class SearchResult(BaseModel):
    content: str
    source: str
    slide: Optional[str] = None
    score: float

# Mock deals data (for BeforeCall tab)
MOCK_DEALS = [
    Deal(
        id=1,
        title="Global Banking Platform Migration",
        summary="Successfully migrated core banking operations to cloud-native architecture with zero downtime",
        solutionArea="Cloud Infrastructure & Digital Transformation",
        industry="Banking & Financial Services",
        benchmark="Banking Solution",
        caseStudy="Enterprise deployed a comprehensive banking platform supporting 500+ branches across 25 countries.",
        teamSize="12 members",
        keyHighlights=["24/7 transaction processing", "Full compliance", "50% cost reduction"],
        dealBreakers=["Strict data residency compliance", "Long sales cycle"],
        dealValue="$2.4M",
        duration="18 months",
    ),
    Deal(
        id=2,
        title="Trade Finance Monitor Implementation",
        summary="AI-powered trade finance monitoring and analytics platform",
        solutionArea="Trade Finance & AI",
        industry="Banking & Financial Services",
        benchmark="Trade Finance Solution",
        caseStudy="Implemented trade finance monitoring system with real-time analytics and compliance tracking.",
        teamSize="8 members",
        keyHighlights=["Real-time monitoring", "AI-driven insights", "Compliance automation"],
        dealBreakers=["Complex integration requirements", "Regulatory approvals needed"],
        dealValue="$1.5M",
        duration="12 months",
    ),
]

# API Endpoints
@app.get("/")
def root():
    return {"message": "DealSense AI API", "status": "running"}

@app.get("/api/deals", response_model=List[Deal])
def get_deals():
    """Get all available deals/case studies"""
    return MOCK_DEALS

@app.get("/api/search")
def search_deals(q: str = "", limit: int = 10):
    """Search deals using RAG semantic search"""
    if not q:
        return MOCK_DEALS[:limit]
    
    # Use RAG semantic search
    try:
        results = semantic_search(q, k=limit)
        search_results = []
        for i, doc in enumerate(results):
            search_results.append({
                "id": i + 1,
                "content": doc.page_content[:500],
                "source": doc.metadata.get("source", "Unknown"),
                "slide": doc.metadata.get("slide", ""),
                "score": 1.0 - (i * 0.1)  # Approximate score based on rank
            })
        return search_results
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    """Query the RAG system with natural language"""
    try:
        answer = answer_query(request.query)
        # Extract sources from the search
        results = semantic_search(request.query, k=3)
        sources = [doc.metadata.get("source", "Unknown") for doc in results]
        return QueryResponse(answer=answer, sources=list(set(sources)))
    except Exception as e:
        return QueryResponse(answer=f"Error: {str(e)}", sources=[])

@app.get("/api/during_call")
def get_during_call():
    """Get during-call context and suggestions"""
    return [
        {
            "id": 1,
            "title": "Trade Finance Capabilities",
            "description": "DXC Trade Finance solution overview",
            "industry": "Banking & Financial Services",
            "teamSize": "10 members",
            "budget": "$1.5M",
            "timeline": "12 months",
            "status": "Active",
            "caseStudy": "Trade finance implementation with AI capabilities",
            "keyHighlights": ["Real-time monitoring", "AI analytics", "Compliance"],
            "dealBreakers": ["Integration complexity"],
            "successCriteria": ["Go-live within timeline", "User adoption > 80%"],
        }
    ]

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
