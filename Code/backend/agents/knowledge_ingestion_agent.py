"""
Knowledge Ingestion Agent for DealSense AI.

A top-level agent that continuously monitors for new knowledge documents
and ingests them into the RAG vector database.

Features:
- Monitors configured document sources (SharePoint, local folders, etc.)
- Automatically processes and embeds new documents
- Tracks ingestion status and history
- Provides real-time status updates via WebSocket
"""
import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from uuid import uuid4
from enum import Enum

from .base_agent import BaseAgent, AgentResult, AgentPhase

logger = logging.getLogger(__name__)

# Storage file for ingestion state
INGESTION_STATE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "ingestion_state.json"
)


class IngestionStatus(str, Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    PROCESSING = "processing"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    ERROR = "error"


class DocumentSource(str, Enum):
    SHAREPOINT = "sharepoint"
    LOCAL_FOLDER = "local_folder"
    MANUAL_UPLOAD = "manual_upload"
    API = "api"


@dataclass
class IngestionJob:
    """Represents a single document ingestion job."""
    id: str
    document_name: str
    source: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    chunks_created: int = 0
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IngestionState:
    """Current state of the Knowledge Ingestion Agent."""
    status: str
    is_running: bool
    last_scan: Optional[str]
    documents_processed: int
    documents_pending: int
    total_chunks: int
    current_job: Optional[Dict[str, Any]]
    recent_jobs: List[Dict[str, Any]]
    sources_configured: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KnowledgeIngestionAgent(BaseAgent):
    """
    Agent that monitors and ingests knowledge documents into the RAG system.
    
    This agent runs as a background process and:
    1. Periodically scans configured sources for new documents
    2. Processes documents (extracts text, sanitizes PII)
    3. Chunks documents appropriately
    4. Generates embeddings and stores in vector DB
    5. Reports status and progress
    """
    
    name = "KnowledgeIngestionAgent"
    
    def __init__(self):
        super().__init__()
        self._is_running = False
        self._current_job: Optional[IngestionJob] = None
        self._state = self._load_state()
        self._scan_interval = 300  # 5 minutes
        self._sources: List[Dict[str, Any]] = []
        self._status_callbacks: List[callable] = []
    
    def _load_state(self) -> Dict[str, Any]:
        """Load persisted state from file."""
        try:
            if os.path.exists(INGESTION_STATE_FILE):
                with open(INGESTION_STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load ingestion state: {e}")
        
        return {
            "status": IngestionStatus.IDLE.value,
            "is_running": False,
            "last_scan": None,
            "documents_processed": 0,
            "total_chunks": 0,
            "recent_jobs": [],
            "sources_configured": [
                {
                    "id": "default_sharepoint",
                    "type": DocumentSource.SHAREPOINT.value,
                    "name": "SharePoint - Sales Documents",
                    "path": "/sites/sales/documents",
                    "enabled": True,
                    "last_sync": None,
                },
                {
                    "id": "local_moms",
                    "type": DocumentSource.LOCAL_FOLDER.value,
                    "name": "Local MoM Archive",
                    "path": "./data/moms",
                    "enabled": True,
                    "last_sync": None,
                },
            ],
        }
    
    def _save_state(self):
        """Persist current state to file."""
        try:
            os.makedirs(os.path.dirname(INGESTION_STATE_FILE), exist_ok=True)
            state = self.get_status()
            with open(INGESTION_STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save ingestion state: {e}")
    
    def add_status_callback(self, callback: callable):
        """Add a callback to be notified of status changes."""
        self._status_callbacks.append(callback)
    
    def _notify_status_change(self):
        """Notify all registered callbacks of a status change."""
        status = self.get_status()
        for callback in self._status_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.error(f"Status callback error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the ingestion agent."""
        return {
            "status": self._state.get("status", IngestionStatus.IDLE.value),
            "is_running": self._is_running,
            "last_scan": self._state.get("last_scan"),
            "documents_processed": self._state.get("documents_processed", 0),
            "documents_pending": len(self._get_pending_documents()),
            "total_chunks": self._state.get("total_chunks", 0),
            "current_job": self._current_job.to_dict() if self._current_job else None,
            "recent_jobs": self._state.get("recent_jobs", [])[-10:],
            "sources_configured": self._state.get("sources_configured", []),
            "scan_interval_seconds": self._scan_interval,
        }
    
    def _get_pending_documents(self) -> List[Dict[str, Any]]:
        """Get list of documents pending ingestion (dummy for demo)."""
        # In production, this would scan actual sources
        return self._state.get("pending_documents", [])
    
    async def start(self):
        """Start the background ingestion loop."""
        if self._is_running:
            logger.info("Knowledge Ingestion Agent already running")
            return
        
        self._is_running = True
        self._state["status"] = IngestionStatus.IDLE.value
        self._state["is_running"] = True
        self._save_state()
        self._notify_status_change()
        
        logger.info("Knowledge Ingestion Agent started")
        
        # Start background loop
        asyncio.create_task(self._run_loop())
    
    async def stop(self):
        """Stop the background ingestion loop."""
        self._is_running = False
        self._state["status"] = IngestionStatus.IDLE.value
        self._state["is_running"] = False
        self._save_state()
        self._notify_status_change()
        logger.info("Knowledge Ingestion Agent stopped")
    
    async def _run_loop(self):
        """Main background loop for scanning and ingesting."""
        while self._is_running:
            try:
                await self._scan_and_ingest()
            except Exception as e:
                logger.error(f"Ingestion loop error: {e}")
                self._state["status"] = IngestionStatus.ERROR.value
                self._notify_status_change()
            
            # Wait before next scan
            await asyncio.sleep(self._scan_interval)
    
    async def _scan_and_ingest(self):
        """Scan for new documents and ingest them."""
        self._state["status"] = IngestionStatus.SCANNING.value
        self._state["last_scan"] = datetime.utcnow().isoformat()
        self._notify_status_change()
        
        # Scan each configured source
        for source in self._state.get("sources_configured", []):
            if not source.get("enabled"):
                continue
            
            new_docs = await self._scan_source(source)
            
            for doc in new_docs:
                await self._ingest_document(doc, source)
        
        self._state["status"] = IngestionStatus.IDLE.value
        self._save_state()
        self._notify_status_change()
    
    async def _scan_source(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scan a source for new documents.
        
        For demo purposes, returns simulated documents.
        In production, would connect to SharePoint/file system.
        """
        # Simulate scanning delay
        await asyncio.sleep(0.5)
        
        # Demo: Return empty list (no new documents)
        # In production, compare against last_sync timestamp
        return []
    
    async def _ingest_document(
        self, 
        document: Dict[str, Any], 
        source: Dict[str, Any]
    ) -> IngestionJob:
        """Ingest a single document into the vector store."""
        job = IngestionJob(
            id=str(uuid4()),
            document_name=document.get("name", "Unknown"),
            source=source.get("type", "unknown"),
            status=IngestionStatus.PROCESSING.value,
            started_at=datetime.utcnow().isoformat(),
        )
        
        self._current_job = job
        self._state["status"] = IngestionStatus.PROCESSING.value
        self._notify_status_change()
        
        try:
            # 1. Extract text from document
            text = await self._extract_text(document)
            
            # 2. Sanitize PII
            sanitized_text = await self._sanitize_text(text)
            
            # 3. Chunk the document
            self._state["status"] = IngestionStatus.EMBEDDING.value
            self._notify_status_change()
            
            chunks = await self._chunk_document(sanitized_text, document)
            
            # 4. Generate embeddings and store
            await self._store_embeddings(chunks, document)
            
            job.status = IngestionStatus.COMPLETED.value
            job.completed_at = datetime.utcnow().isoformat()
            job.chunks_created = len(chunks)
            
            self._state["documents_processed"] += 1
            self._state["total_chunks"] += len(chunks)
            
        except Exception as e:
            job.status = IngestionStatus.ERROR.value
            job.error_message = str(e)
            logger.error(f"Document ingestion failed: {e}")
        
        # Add to recent jobs
        if "recent_jobs" not in self._state:
            self._state["recent_jobs"] = []
        self._state["recent_jobs"].append(job.to_dict())
        self._state["recent_jobs"] = self._state["recent_jobs"][-50:]  # Keep last 50
        
        self._current_job = None
        self._save_state()
        self._notify_status_change()
        
        return job
    
    async def _extract_text(self, document: Dict[str, Any]) -> str:
        """Extract text from document (dummy implementation)."""
        await asyncio.sleep(0.2)  # Simulate processing
        return document.get("content", "")
    
    async def _sanitize_text(self, text: str) -> str:
        """Sanitize PII from text (dummy implementation)."""
        await asyncio.sleep(0.1)  # Simulate processing
        # In production, use privacy.sanitizer
        return text
    
    async def _chunk_document(
        self, 
        text: str, 
        document: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Chunk document for embedding (dummy implementation)."""
        await asyncio.sleep(0.1)  # Simulate processing
        # In production, use ingestion.deal_ingestion
        chunk_size = 1000
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append({
                "content": text[i:i+chunk_size],
                "metadata": {
                    "source": document.get("name"),
                    "chunk_index": len(chunks),
                },
            })
        return chunks if chunks else [{"content": text, "metadata": {}}]
    
    async def _store_embeddings(
        self, 
        chunks: List[Dict[str, Any]], 
        document: Dict[str, Any]
    ):
        """Store embeddings in vector DB (dummy implementation)."""
        await asyncio.sleep(0.3)  # Simulate embedding generation
        # In production, use retrieval.semantic_search.load_vector_store
        logger.info(f"Stored {len(chunks)} chunks for {document.get('name')}")
    
    # -------------------------------------------------------------------------
    # Manual ingestion methods (for demo/UI)
    # -------------------------------------------------------------------------
    
    async def ingest_manual(
        self,
        content: str,
        document_name: str,
        document_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> IngestionJob:
        """
        Manually ingest a document (for demo purposes).
        
        Args:
            content: Document text content
            document_name: Name of the document
            document_type: Type of document (text, mom, case_study, etc.)
            metadata: Additional metadata
            
        Returns:
            IngestionJob with result
        """
        document = {
            "name": document_name,
            "content": content,
            "type": document_type,
            "metadata": metadata or {},
        }
        
        source = {
            "type": DocumentSource.MANUAL_UPLOAD.value,
            "name": "Manual Upload",
        }
        
        return await self._ingest_document(document, source)
    
    async def add_source(
        self,
        source_type: str,
        name: str,
        path: str,
        enabled: bool = True,
    ) -> Dict[str, Any]:
        """Add a new document source to monitor."""
        new_source = {
            "id": str(uuid4()),
            "type": source_type,
            "name": name,
            "path": path,
            "enabled": enabled,
            "last_sync": None,
        }
        
        self._state["sources_configured"].append(new_source)
        self._save_state()
        self._notify_status_change()
        
        return new_source
    
    async def remove_source(self, source_id: str) -> bool:
        """Remove a document source."""
        sources = self._state.get("sources_configured", [])
        self._state["sources_configured"] = [
            s for s in sources if s.get("id") != source_id
        ]
        self._save_state()
        return True
    
    async def toggle_source(self, source_id: str, enabled: bool) -> bool:
        """Enable or disable a document source."""
        for source in self._state.get("sources_configured", []):
            if source.get("id") == source_id:
                source["enabled"] = enabled
                self._save_state()
                return True
        return False
    
    # -------------------------------------------------------------------------
    # BaseAgent abstract method implementations
    # -------------------------------------------------------------------------
    
    async def perceive(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the incoming request."""
        return {
            "action": request.get("action", "status"),
            "content": request.get("content"),
            "document_name": request.get("document_name"),
            "source_id": request.get("source_id"),
        }
    
    async def plan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan actions based on request."""
        action = context.get("action")
        
        if action == "ingest":
            return [{"tool": "manual_ingest", "params": context}]
        elif action == "start":
            return [{"tool": "start_agent", "params": {}}]
        elif action == "stop":
            return [{"tool": "stop_agent", "params": {}}]
        else:
            return [{"tool": "get_status", "params": {}}]
    
    async def execute_tools(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute planned tool calls."""
        results = {}
        
        for step in plan:
            tool = step.get("tool")
            params = step.get("params", {})
            
            if tool == "manual_ingest":
                job = await self.ingest_manual(
                    content=params.get("content", ""),
                    document_name=params.get("document_name", "Untitled"),
                )
                results["job"] = job.to_dict()
            elif tool == "start_agent":
                await self.start()
                results["started"] = True
            elif tool == "stop_agent":
                await self.stop()
                results["stopped"] = True
            else:
                results["status"] = self.get_status()
        
        return results
    
    async def reflect(
        self, 
        context: Dict[str, Any], 
        tool_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate results."""
        return {
            "success": True,
            "confidence": 1.0,
        }
    
    async def act(
        self,
        context: Dict[str, Any],
        tool_results: Dict[str, Any],
        reflection: Dict[str, Any],
    ) -> AgentResult:
        """Produce final result."""
        return AgentResult(
            success=reflection.get("success", True),
            output=tool_results,
            confidence=reflection.get("confidence", 1.0),
        )


# Singleton instance
_knowledge_agent: Optional[KnowledgeIngestionAgent] = None


def get_knowledge_agent() -> KnowledgeIngestionAgent:
    """Get or create the knowledge ingestion agent singleton."""
    global _knowledge_agent
    if _knowledge_agent is None:
        _knowledge_agent = KnowledgeIngestionAgent()
    return _knowledge_agent
