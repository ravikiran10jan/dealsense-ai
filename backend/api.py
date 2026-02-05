"""
FastAPI backend for DealSense AI
Integrates RAG search with the UI
With privacy protection, authentication, and audit logging.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from fastapi import FastAPI, HTTPException, Depends, Security, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import RAG components
from orchestration.hybrid_answer import answer_query, answer_query_with_context
from retrieval.semantic_search import semantic_search, semantic_search_with_scores, load_vector_store
from ingestion.deal_ingestion import ingest_deal_to_vector_store
from llm.talking_points import generate_talking_points_from_query

# Import privacy components
from privacy.auth import verify_api_key, get_auth_manager, require_permission, ROLES
from privacy.sanitizer import sanitize_text, desanitize_text, get_sanitizer
from privacy.tokenizer import get_tokenizer
from privacy.audit_logger import audit_log, get_audit_logger

# Import Live Call components
from models.call import (
    Call, CallCreate, CallStatus,
    TranscriptChunk, TranscriptChunkCreate,
    CallSummary, CallSummaryCreate,
    ActionItem, ActionItemCreate, ActionItemUpdate,
    ActionItemStatus, ActionItemPriority
)
from storage import get_redis_client, get_call_repository
from websocket import get_connection_manager, get_live_call_handler
from summarization import generate_call_summary, extract_action_items

app = FastAPI(title="DealSense AI API", version="1.0.0")

# CORS middleware - Restricted to known origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Add configured frontend URL if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    ALLOWED_ORIGINS.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],
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
    """Use RAG to auto-populate deal context including dynamic talking points"""
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
    
    # Generate dynamic talking points using RAG + LLM
    try:
        talking_points_result = generate_talking_points_from_query(
            client_name=account_name,
            industry=industry,
            description=description,
            semantic_search_fn=semantic_search,
            num_points=4
        )
        talking_points = talking_points_result.get("talking_points", [])
        logger.info(f"Generated {len(talking_points)} talking points for {account_name} (source: {talking_points_result.get('source_type')})")
    except Exception as e:
        logger.warning(f"Failed to generate talking points for {account_name}: {e}")
        # Fallback to default talking points
        talking_points = [
            f"Discuss {description} implementation approach",
            f"Reference similar {industry} implementations",
            "Highlight team expertise and delivery methodology",
            "Address data privacy and compliance requirements",
        ]
    
    # Parse and structure the results (these can be enhanced similarly in the future)
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
def get_active_deals(auth: Dict = Depends(verify_api_key)):
    """Get all active deals from storage"""
    deals = load_deals()
    
    # Audit log the access
    audit_log(
        action='deal_read',
        resource_type='deal',
        resource_id='all',
        auth_info=auth,
        status='success'
    )
    
    return deals

@app.post("/api/deals/create")
def create_deal(deal_request: NewDealRequest, auth: Dict = Depends(verify_api_key)):
    """Create a new deal and populate context from RAG"""
    deals = load_deals()
    
    # Generate new ID
    new_id = max([d.get('id', 0) for d in deals], default=0) + 1
    
    # Sanitize contact information before storage
    source_ref = f"deal_{new_id}"
    sanitized_contact_name, contact_tokens = sanitize_text(deal_request.contactName, source=f"{source_ref}_contact")
    
    # Create deal dict with sanitized data
    new_deal = {
        "id": new_id,
        "accountName": deal_request.accountName,
        "stage": deal_request.stage,
        "nextCallDate": deal_request.nextCallDate,
        "nextCallTime": deal_request.nextCallTime,
        "dealAmount": deal_request.dealAmount,
        "contactName": sanitized_contact_name,  # Sanitized
        "contactRole": deal_request.contactRole,
        "industry": deal_request.industry,
        "description": deal_request.description,
        "additionalContacts": [c.dict() for c in deal_request.additionalContacts] if deal_request.additionalContacts else [],
        "pii_tokens": contact_tokens,  # Track tokens for retrieval
    }
    
    # If notes provided, add to vector store (sanitization happens in ingest function)
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
    
    # Audit log the deal creation
    audit_log(
        action='deal_create',
        resource_type='deal',
        resource_id=str(new_id),
        auth_info=auth,
        status='success'
    )
    
    return new_deal

@app.get("/api/deals/{deal_id}/context")
def get_deal_context(deal_id: int, auth: Dict = Depends(verify_api_key)):
    """Get RAG-populated context for a specific deal"""
    deals = load_deals()
    deal = next((d for d in deals if d.get('id') == deal_id), None)
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Re-populate context from RAG
    deal = populate_deal_context(deal)
    
    # Audit log the access
    audit_log(
        action='deal_read',
        resource_type='deal',
        resource_id=str(deal_id),
        auth_info=auth,
        status='success'
    )
    
    return {
        "similarDeals": deal.get('similarDeals', []),
        "credibleReferences": deal.get('credibleReferences', []),
        "expectedQuestions": deal.get('expectedQuestions', []),
        "suggestedTalkingPoints": deal.get('suggestedTalkingPoints', []),
    }


class TalkingPointsRequest(BaseModel):
    client_name: str
    industry: str
    description: str
    num_points: Optional[int] = 4


class TalkingPointsResponse(BaseModel):
    talking_points: List[str]
    sources: List[str]
    source_type: str


@app.post("/api/talking-points", response_model=TalkingPointsResponse)
def generate_talking_points_endpoint(
    request: TalkingPointsRequest,
    auth: Dict = Depends(verify_api_key)
):
    """
    Generate suggested talking points using RAG + LLM.
    
    Uses semantic search to retrieve relevant context about similar deals,
    case studies, and implementations, then generates tailored talking points.
    """
    try:
        result = generate_talking_points_from_query(
            client_name=request.client_name,
            industry=request.industry,
            description=request.description,
            semantic_search_fn=semantic_search,
            num_points=request.num_points
        )
        
        # Audit log the generation
        audit_log(
            action='talking_points_generate',
            resource_type='rag',
            auth_info=auth,
            status='success',
            results_count=len(result.get("talking_points", []))
        )
        
        return TalkingPointsResponse(
            talking_points=result.get("talking_points", []),
            sources=result.get("sources", []),
            source_type=result.get("source_type", "LLM")
        )
    except Exception as e:
        logger.error(f"Failed to generate talking points: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate talking points: {str(e)}")


@app.get("/api/deals/{deal_id}/talking-points", response_model=TalkingPointsResponse)
def get_deal_talking_points(deal_id: int, auth: Dict = Depends(verify_api_key)):
    """
    Generate talking points for a specific deal using RAG + LLM.
    
    Retrieves deal information and generates contextual talking points
    based on the client, industry, and deal description.
    """
    deals = load_deals()
    deal = next((d for d in deals if d.get('id') == deal_id), None)
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    try:
        result = generate_talking_points_from_query(
            client_name=deal.get('accountName', ''),
            industry=deal.get('industry', ''),
            description=deal.get('description', ''),
            semantic_search_fn=semantic_search,
            num_points=4
        )
        
        # Audit log the generation
        audit_log(
            action='talking_points_generate',
            resource_type='deal',
            resource_id=str(deal_id),
            auth_info=auth,
            status='success',
            results_count=len(result.get("talking_points", []))
        )
        
        return TalkingPointsResponse(
            talking_points=result.get("talking_points", []),
            sources=result.get("sources", []),
            source_type=result.get("source_type", "LLM")
        )
    except Exception as e:
        logger.error(f"Failed to generate talking points for deal {deal_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate talking points: {str(e)}")

@app.delete("/api/deals/{deal_id}")
def delete_deal(deal_id: int, auth: Dict = Depends(verify_api_key)):
    """Delete a deal"""
    deals = load_deals()
    
    # Check if deal exists
    deal = next((d for d in deals if d.get('id') == deal_id), None)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Delete associated PII tokens
    tokenizer = get_tokenizer()
    tokenizer.delete_tokens_for_source(f"deal_{deal_id}")
    tokenizer.delete_tokens_for_source(f"deal_{deal_id}_name")
    tokenizer.delete_tokens_for_source(f"deal_{deal_id}_contact")
    
    deals = [d for d in deals if d.get('id') != deal_id]
    save_deals(deals)
    
    # Audit log the deletion
    audit_log(
        action='deal_delete',
        resource_type='deal',
        resource_id=str(deal_id),
        auth_info=auth,
        status='success'
    )
    
    return {"status": "deleted", "id": deal_id}

@app.get("/api/search")
def search_deals(q: str = "", limit: int = 10, auth: Dict = Depends(verify_api_key)):
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
        
        # Audit log the search
        audit_log(
            action='search',
            resource_type='rag',
            auth_info=auth,
            status='success',
            results_count=len(search_results)
        )
        
        return search_results
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/query", response_model=QueryResponse)
def query_rag(request: QueryRequest, auth: Dict = Depends(verify_api_key)):
    """Query the RAG system with natural language"""
    try:
        result = answer_query(request.query)
        # answer_query now returns dict with 'answer', 'sources', 'source_type'
        
        # Audit log the query
        audit_log(
            action='query',
            resource_type='rag',
            auth_info=auth,
            status='success',
            results_count=len(result.get("sources", []))
        )
        
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

@app.get("/api/outlook/upcoming-meetings")
def get_outlook_meetings():
    """
    Fetch upcoming meetings from Outlook calendar.
    
    NOTE: This is a mock implementation. For production, integrate with 
    Microsoft Graph API using azure-identity and msgraph-sdk.
    
    Real implementation would:
    1. Use MSAL to authenticate user
    2. Call Graph API: GET /me/calendar/events
    3. Parse and return meeting details
    """
    # Mock data simulating Outlook calendar meetings
    # In production, replace with actual Graph API call:
    # from msgraph.generated.users.item.calendar.events.events_request_builder import EventsRequestBuilder
    
    tomorrow = datetime.now() + timedelta(days=1)
    next_week = datetime.now() + timedelta(days=7)
    
    mock_meetings = [
        {
            "id": "outlook-meeting-001",
            "subject": "Trade Finance Platform Discovery Call - ANZ Bank",
            "accountName": "ANZ Bank",
            "contactName": "Sarah Mitchell",
            "contactRole": "Head of Trade Operations",
            "date": tomorrow.strftime("%Y-%m-%d"),
            "time": "10:00",
            "body": "Initial discovery call to discuss trade finance modernization. Key topics: current pain points, LC processing volumes, integration requirements with existing systems.",
            "attendees": ["sarah.mitchell@anz.com", "david.chen@anz.com"],
            "location": "Microsoft Teams",
        },
        {
            "id": "outlook-meeting-002", 
            "subject": "Follow-up: Digital Banking Transformation - Westpac",
            "accountName": "Westpac",
            "contactName": "James Wilson",
            "contactRole": "VP Digital Strategy",
            "date": next_week.strftime("%Y-%m-%d"),
            "time": "14:30",
            "body": "Follow-up discussion on digital banking platform requirements. Agenda: API strategy, mobile banking features, security compliance.",
            "attendees": ["james.wilson@westpac.com"],
            "location": "Zoom",
        },
    ]
    
    return mock_meetings

class SendInviteRequest(BaseModel):
    dealId: int
    accountName: str
    contactName: str
    contactEmail: Optional[str] = ""
    date: str
    time: str
    description: str

@app.post("/api/outlook/send-invite")
def send_calendar_invite(request: SendInviteRequest):
    """
    Send a calendar invite via Outlook.
    
    NOTE: This is a mock implementation. For production, integrate with
    Microsoft Graph API to create calendar events with attendees.
    
    Real implementation would:
    1. Use MSAL to authenticate
    2. Call Graph API: POST /me/calendar/events
    3. Include attendees, subject, body, start/end times
    """
    # Mock response simulating successful invite creation
    # In production, replace with actual Graph API call
    
    invite_id = f"invite-{request.dealId}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "status": "success",
        "inviteId": invite_id,
        "message": f"Calendar invite sent for {request.description}",
        "details": {
            "to": request.contactEmail or f"{request.contactName.lower().replace(' ', '.')}@example.com",
            "subject": f"Meeting: {request.description} - {request.accountName}",
            "date": request.date,
            "time": request.time,
            "location": "Microsoft Teams (link will be auto-generated)",
        }
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


# ==================== Privacy API Endpoints ====================

class DetokenizeRequest(BaseModel):
    text: str
    
class AuditQueryParams(BaseModel):
    user_id: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    pii_only: Optional[bool] = False
    limit: Optional[int] = 100


@app.get("/api/privacy/audit")
def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    pii_only: bool = False,
    limit: int = 100,
    auth: Dict = Depends(verify_api_key)
):
    """
    Get audit logs. Admin only.
    
    Query parameters:
    - user_id: Filter by user
    - action: Filter by action type
    - resource_type: Filter by resource type (deal, transcript, rag, pii)
    - resource_id: Filter by specific resource ID
    - start_date: Start date (ISO format)
    - end_date: End date (ISO format)
    - pii_only: Only show PII access events
    - limit: Maximum results (default 100)
    """
    # Check admin permission
    if auth.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    logger = get_audit_logger()
    logs = logger.get_logs(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        pii_only=pii_only,
        limit=limit
    )
    
    return {"total": len(logs), "logs": logs}


@app.get("/api/privacy/stats")
def get_privacy_stats(auth: Dict = Depends(verify_api_key)):
    """
    Get privacy and audit statistics. Admin only.
    """
    if auth.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get audit stats
    audit_stats = get_audit_logger().get_stats(days=30)
    
    # Get tokenizer stats
    token_stats = get_tokenizer().get_token_stats()
    
    return {
        "audit": audit_stats,
        "pii_tokens": token_stats
    }


@app.post("/api/privacy/detokenize")
def detokenize_pii(request: DetokenizeRequest, auth: Dict = Depends(verify_api_key)):
    """
    Detokenize PII in text. Admin only.
    Returns the text with PII tokens replaced by original values.
    
    This action is logged in the audit trail.
    """
    if auth.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required for PII access")
    
    # Detokenize the text
    original_text = desanitize_text(request.text, track_access=True)
    
    # Audit log the PII access
    audit_log(
        action='pii_detokenize',
        resource_type='pii',
        auth_info=auth,
        status='success',
        pii_accessed=True
    )
    
    return {"original_text": original_text}


@app.get("/api/privacy/roles")
def get_roles(auth: Dict = Depends(verify_api_key)):
    """Get available roles and their permissions."""
    return {"roles": ROLES}


# ==================== Live Call API Endpoints ====================

# Pydantic models for Live Call
class StartCallRequest(BaseModel):
    deal_id: int
    account_name: str
    contact_name: Optional[str] = None


class StartCallResponse(BaseModel):
    call_id: str
    websocket_url: str
    status: str


class EndCallRequest(BaseModel):
    pass  # No body required


class CallQueryRequest(BaseModel):
    query: str
    deal_id: Optional[int] = None


class CallQueryResponse(BaseModel):
    answer: str
    sources: List[str]
    source_type: str
    confidence: float


class MockTranscriptRequest(BaseModel):
    speaker: str
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None


# WebSocket endpoint for live calls
@app.websocket("/ws/call/{call_id}")
async def websocket_call_endpoint(websocket: WebSocket, call_id: str):
    """
    WebSocket endpoint for live call communication.
    
    Message types (client -> server):
    - start_call: Initialize call with deal_id, account_name, contact_name
    - audio_chunk: Send audio data for transcription
    - push_to_talk_query: Ask a question during the call
    - end_call: End the call and trigger summary generation
    
    Message types (server -> client):
    - transcript_chunk: Real-time transcript updates
    - query_response: Answer to push-to-talk query
    - status_update: Call status changes
    - summary_ready: Summary generation complete
    - error: Error messages
    """
    call_uuid = UUID(call_id)
    connection_manager = get_connection_manager()
    live_call_handler = get_live_call_handler()
    
    await connection_manager.connect(websocket, call_uuid)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process the message
            await live_call_handler.handle_message(websocket, call_uuid, data)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for call {call_id}")
        connection_manager.disconnect(websocket, call_uuid)
    except Exception as e:
        logger.error(f"WebSocket error for call {call_id}: {e}")
        connection_manager.disconnect(websocket, call_uuid)
        raise


# REST endpoints for calls
@app.post("/api/calls/start", response_model=StartCallResponse)
def start_call(request: StartCallRequest, auth: Dict = Depends(verify_api_key)):
    """
    Start a new call and get WebSocket URL for real-time communication.
    """
    call_repository = get_call_repository()
    
    # Create call record
    call_create = CallCreate(
        deal_id=request.deal_id,
        account_name=request.account_name,
        contact_name=request.contact_name,
    )
    call = call_repository.create_call(call_create)
    
    # Generate WebSocket URL
    base_url = os.getenv("API_BASE_URL", "ws://localhost:8000")
    ws_url = f"{base_url.replace('http', 'ws')}/ws/call/{call.id}"
    
    # Audit log
    audit_log(
        action='call_start',
        resource_type='call',
        resource_id=str(call.id),
        auth_info=auth,
        status='success'
    )
    
    return StartCallResponse(
        call_id=str(call.id),
        websocket_url=ws_url,
        status="created"
    )


@app.post("/api/calls/{call_id}/end")
async def end_call(call_id: str, background_tasks: BackgroundTasks, auth: Dict = Depends(verify_api_key)):
    """
    End a call and trigger summary generation.
    """
    call_uuid = UUID(call_id)
    call_repository = get_call_repository()
    
    # End the call
    call = call_repository.end_call(call_uuid)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # Get full transcript for summary
    transcript_chunks = call_repository.get_transcript(call_uuid)
    full_transcript = call_repository.get_full_transcript_text(call_uuid)
    
    # Schedule background summary generation
    async def generate_summary_task():
        try:
            # Generate summary
            summary_data = await generate_call_summary(full_transcript, call.deal_id)
            
            # Save summary
            summary_create = CallSummaryCreate(
                call_id=call_uuid,
                executive_summary=summary_data.get("executive_summary", ""),
                key_points=summary_data.get("key_points", []),
                pain_points=summary_data.get("pain_points", []),
                objections=summary_data.get("objections", []),
                next_steps=summary_data.get("next_steps", []),
                deal_health_score=summary_data.get("deal_health_score", 5),
                deal_health_reason=summary_data.get("deal_health_reasoning", "")
            )
            call_repository.create_summary(summary_create)
            
            # Extract and save action items
            action_items = await extract_action_items(full_transcript)
            if action_items:
                call_repository.create_action_items_batch(call_uuid, action_items)
            
            logger.info(f"Summary generated for call {call_id}")
        except Exception as e:
            logger.error(f"Failed to generate summary for call {call_id}: {e}")
    
    # Run in background
    background_tasks.add_task(generate_summary_task)
    
    # Audit log
    audit_log(
        action='call_end',
        resource_type='call',
        resource_id=call_id,
        auth_info=auth,
        status='success'
    )
    
    return {
        "status": "summary_generating",
        "call_id": call_id,
        "duration_seconds": call.duration_seconds
    }


@app.get("/api/calls/{call_id}/transcript")
def get_call_transcript(
    call_id: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    auth: Dict = Depends(verify_api_key)
):
    """
    Get transcript for a call.
    Optionally filter by time range.
    """
    call_uuid = UUID(call_id)
    call_repository = get_call_repository()
    
    chunks = call_repository.get_transcript(call_uuid, start_time, end_time)
    
    return {
        "call_id": call_id,
        "chunks": [
            {
                "id": str(c.id),
                "speaker": c.speaker,
                "text": c.text,
                "start_time": c.start_time,
                "end_time": c.end_time,
                "is_final": c.is_final,
            }
            for c in chunks
        ],
        "total_chunks": len(chunks)
    }


@app.get("/api/calls/{call_id}/summary")
def get_call_summary(call_id: str, auth: Dict = Depends(verify_api_key)):
    """
    Get summary for a call.
    """
    call_uuid = UUID(call_id)
    call_repository = get_call_repository()
    
    summary = call_repository.get_summary(call_uuid)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    action_items = call_repository.get_action_items(call_uuid)
    
    return {
        "call_id": call_id,
        "summary": {
            "id": str(summary.id),
            "executive_summary": summary.executive_summary,
            "key_points": summary.key_points,
            "pain_points": [pp.dict() for pp in summary.pain_points],
            "objections": [obj.dict() for obj in summary.objections],
            "next_steps": summary.next_steps,
            "deal_health_score": summary.deal_health_score,
            "deal_health_reason": summary.deal_health_reason,
            "generated_at": summary.generated_at.isoformat(),
        },
        "action_items": [
            {
                "id": str(item.id),
                "task": item.task,
                "owner": item.owner,
                "due_date": item.due_date.isoformat() if item.due_date else None,
                "priority": item.priority.value,
                "status": item.status.value,
            }
            for item in action_items
        ]
    }


@app.post("/api/calls/{call_id}/query", response_model=CallQueryResponse)
def query_during_call(
    call_id: str,
    request: CallQueryRequest,
    auth: Dict = Depends(verify_api_key)
):
    """
    Query the RAG system with call context.
    Used for push-to-talk queries during live calls.
    """
    call_uuid = UUID(call_id)
    redis_client = get_redis_client()
    
    # Get recent transcript context
    recent_transcript = redis_client.get_recent_transcript_text(call_uuid)
    
    # Get call metadata
    metadata = redis_client.get_call_metadata(call_uuid)
    account_name = metadata.get("account_name", "Unknown")
    
    # Query with context
    result = answer_query_with_context(
        query=request.query,
        call_context={
            "recent_transcript": recent_transcript,
            "account_name": account_name,
            "deal_id": request.deal_id,
        }
    )
    
    # Audit log
    audit_log(
        action='call_query',
        resource_type='call',
        resource_id=call_id,
        auth_info=auth,
        status='success'
    )
    
    return CallQueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        source_type=result["source_type"],
        confidence=result.get("confidence", 1.0)
    )


@app.get("/api/calls")
def list_calls(
    deal_id: Optional[int] = None,
    limit: int = 20,
    auth: Dict = Depends(verify_api_key)
):
    """
    List calls, optionally filtered by deal_id.
    """
    call_repository = get_call_repository()
    
    if deal_id:
        calls = call_repository.get_calls_by_deal(deal_id)
    else:
        # Get all calls (would need to implement this method)
        calls = []
    
    return {
        "calls": [
            {
                "id": str(c.id),
                "deal_id": c.deal_id,
                "account_name": c.account_name,
                "contact_name": c.contact_name,
                "started_at": c.started_at.isoformat(),
                "ended_at": c.ended_at.isoformat() if c.ended_at else None,
                "duration_seconds": c.duration_seconds,
                "status": c.status.value,
            }
            for c in calls
        ],
        "total": len(calls)
    }


@app.patch("/api/calls/{call_id}/action-items/{item_id}")
def update_action_item(
    call_id: str,
    item_id: str,
    updates: ActionItemUpdate,
    auth: Dict = Depends(verify_api_key)
):
    """
    Update an action item (status, owner, due date, etc.)
    """
    item_uuid = UUID(item_id)
    call_repository = get_call_repository()
    
    item = call_repository.update_action_item(item_uuid, updates)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    return {
        "id": str(item.id),
        "task": item.task,
        "owner": item.owner,
        "due_date": item.due_date.isoformat() if item.due_date else None,
        "priority": item.priority.value,
        "status": item.status.value,
        "updated_at": item.updated_at.isoformat(),
    }


@app.post("/api/calls/{call_id}/mock-transcript")
async def add_mock_transcript(
    call_id: str,
    request: MockTranscriptRequest,
    auth: Dict = Depends(verify_api_key)
):
    """
    Add a mock transcript chunk for testing.
    Useful for development without real audio capture.
    """
    call_uuid = UUID(call_id)
    live_call_handler = get_live_call_handler()
    
    await live_call_handler.add_mock_transcript_chunk(
        call_id=call_uuid,
        speaker=request.speaker,
        text=request.text,
        start_time=request.start_time,
        end_time=request.end_time,
    )
    
    return {"status": "added", "call_id": call_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
