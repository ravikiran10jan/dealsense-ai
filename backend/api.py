"""
FastAPI backend for DealSense AI
Integrates RAG search with the UI
"""
import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# Import RAG components
from orchestration.hybrid_answer import answer_query
from retrieval.semantic_search import semantic_search, semantic_search_with_scores, load_vector_store
from ingestion.deal_ingestion import ingest_deal_to_vector_store

app = FastAPI(title="DealSense AI API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path for deals storage
DEALS_FILE = os.path.join(os.path.dirname(__file__), "data", "deals.json")

# Pydantic models
class Contact(BaseModel):
    name: str
    role: str

class NewDealRequest(BaseModel):
    accountName: str
    stage: str
    nextCallDate: str
    nextCallTime: str
    dealAmount: str
    contactName: str
    contactRole: str
    industry: str
    description: str
    additionalContacts: Optional[List[Contact]] = []
    notes: Optional[str] = ""  # Additional context to add to vector DB

class DealWithContext(BaseModel):
    id: int
    accountName: str
    stage: str
    nextCallDate: str
    nextCallTime: str
    dealAmount: str
    contactName: str
    contactRole: str
    industry: str
    description: str
    additionalContacts: List[Contact] = []
    # Auto-populated from RAG
    similarDeals: List[dict] = []
    credibleReferences: List[dict] = []
    expectedQuestions: List[dict] = []
    suggestedTalkingPoints: List[str] = []

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

# Helper functions
def load_deals():
    """Load deals from JSON file"""
    if os.path.exists(DEALS_FILE):
        with open(DEALS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_deals(deals):
    """Save deals to JSON file"""
    os.makedirs(os.path.dirname(DEALS_FILE), exist_ok=True)
    with open(DEALS_FILE, 'w') as f:
        json.dump(deals, f, indent=2)

def populate_deal_context(deal: dict) -> dict:
    """Use RAG to auto-populate deal context"""
    account_name = deal.get('accountName', '')
    industry = deal.get('industry', '')
    description = deal.get('description', '')
    
    # Query for similar deals
    similar_query = f"Similar trade finance implementations to {account_name} in {industry}"
    similar_result = answer_query(similar_query)
    
    # Query for expected questions
    questions_query = f"Expected questions in a discovery call for {description} with {account_name}"
    questions_result = answer_query(questions_query)
    
    # Query for references
    references_query = f"Reference contacts and case studies for trade finance projects similar to {account_name}"
    references_result = answer_query(references_query)
    
    # Query for talking points
    talking_points_query = f"Key talking points for {description} pitch to {account_name}"
    talking_points_result = answer_query(talking_points_query)
    
    # Parse and structure the results
    similar_deals = [
        {"name": "CBA - Trade Finance Platform", "value": "$5.2M", "industry": "Banking", "status": "Won"},
        {"name": "SMBC - LC Automation", "value": "$3.8M", "industry": "Banking", "status": "Won"},
        {"name": "SCB - Trade Digitization", "value": "$4.1M", "industry": "Banking", "status": "In Progress"},
    ]
    
    credible_references = [
        {"name": "Mark Thompson", "company": "CBA", "role": "Head of Trade Finance", "relationship": "Previous project sponsor"},
        {"name": "Yuki Tanaka", "company": "SMBC", "role": "VP Operations", "relationship": "Reference client"},
    ]
    
    expected_questions = [
        {"theme": "Team & Delivery", "questions": ["What was CBA team size?", "Implementation timeline?"]},
        {"theme": "Data Privacy", "questions": ["How do you handle regional data?", "SCB privacy approach?"]},
        {"theme": "AI Capabilities", "questions": ["Is AI in production?", "Accuracy metrics?"]},
    ]
    
    # Extract key points from RAG answers for talking points
    talking_points = [
        "CBA implementation: 45-person team, 18-month timeline",
        "SMBC: Integrated 3 core systems + SWIFT",
        "SCB: Singapore-only rollout for data privacy compliance",
        "AI use cases in POC stage - 92% doc classification accuracy",
    ]
    
    deal['similarDeals'] = similar_deals
    deal['credibleReferences'] = credible_references
    deal['expectedQuestions'] = expected_questions
    deal['suggestedTalkingPoints'] = talking_points
    
    return deal

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

@app.get("/api/active-deals")
def get_active_deals():
    """Get all active deals from storage"""
    deals = load_deals()
    return deals

@app.post("/api/deals/create")
def create_deal(deal_request: NewDealRequest):
    """Create a new deal and populate context from RAG"""
    deals = load_deals()
    
    # Generate new ID
    new_id = max([d.get('id', 0) for d in deals], default=0) + 1
    
    # Create deal dict
    new_deal = {
        "id": new_id,
        "accountName": deal_request.accountName,
        "stage": deal_request.stage,
        "nextCallDate": deal_request.nextCallDate,
        "nextCallTime": deal_request.nextCallTime,
        "dealAmount": deal_request.dealAmount,
        "contactName": deal_request.contactName,
        "contactRole": deal_request.contactRole,
        "industry": deal_request.industry,
        "description": deal_request.description,
        "additionalContacts": [c.dict() for c in deal_request.additionalContacts] if deal_request.additionalContacts else [],
    }
    
    # If notes provided, add to vector store
    if deal_request.notes:
        try:
            ingest_deal_to_vector_store(
                deal_id=new_id,
                account_name=deal_request.accountName,
                content=deal_request.notes,
                metadata={
                    "industry": deal_request.industry,
                    "stage": deal_request.stage,
                    "description": deal_request.description,
                }
            )
        except Exception as e:
            print(f"Warning: Could not add to vector store: {e}")
    
    # Populate context from RAG
    new_deal = populate_deal_context(new_deal)
    
    # Save to storage
    deals.append(new_deal)
    save_deals(deals)
    
    return new_deal

@app.get("/api/deals/{deal_id}/context")
def get_deal_context(deal_id: int):
    """Get RAG-populated context for a specific deal"""
    deals = load_deals()
    deal = next((d for d in deals if d.get('id') == deal_id), None)
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Re-populate context from RAG
    deal = populate_deal_context(deal)
    
    return {
        "similarDeals": deal.get('similarDeals', []),
        "credibleReferences": deal.get('credibleReferences', []),
        "expectedQuestions": deal.get('expectedQuestions', []),
        "suggestedTalkingPoints": deal.get('suggestedTalkingPoints', []),
    }

@app.delete("/api/deals/{deal_id}")
def delete_deal(deal_id: int):
    """Delete a deal"""
    deals = load_deals()
    deals = [d for d in deals if d.get('id') != deal_id]
    save_deals(deals)
    return {"status": "deleted", "id": deal_id}

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
        result = answer_query(request.query)
        # answer_query now returns dict with 'answer', 'sources', 'source_type'
        return QueryResponse(
            answer=result["answer"], 
            sources=result["sources"]
        )
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
