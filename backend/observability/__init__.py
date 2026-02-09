"""
Observability & Evaluation module for DealSense AI.

Provides LLM tracing via Opik, experiment tracking,
and evaluation pipelines for RAG and agent quality.
"""
from .opik_config import configure_opik, get_opik_client, is_opik_enabled
from .opik_tracer import (
    track_rag_query,
    track_agent_action,
    track_api_endpoint,
    log_event,
    setup_openai_tracking,
    OpikTrace,
)
from .evaluation import (
    create_rag_dataset,
    run_rag_evaluation,
    run_agent_evaluation,
    list_experiments,
)

__all__ = [
    # Config
    "configure_opik",
    "get_opik_client",
    "is_opik_enabled",
    # Tracers
    "track_rag_query",
    "track_agent_action",
    "track_api_endpoint",
    "log_event",
    "setup_openai_tracking",
    "OpikTrace",
    # Evaluation
    "create_rag_dataset",
    "run_rag_evaluation",
    "run_agent_evaluation",
    "list_experiments",
]
