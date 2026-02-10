"""
Opik Observability Tracers for DealSense AI.

Provides domain-specific tracking decorators for:
  - RAG queries  (track_rag_query)
  - Agent actions (track_agent_action)
  - API endpoints (track_api_endpoint)
  - Custom events (log_event)
  - Manual traces (OpikTrace context manager)

All decorators degrade to no-ops when OPIK_ENABLED != "true".
"""
import os
import time
import logging
from typing import Optional, Dict, Any, List
from functools import wraps

from .opik_config import is_opik_enabled, get_opik_client

logger = logging.getLogger(__name__)

OPIK_ENABLED = is_opik_enabled()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _noop_decorator(**_kwargs):
    """Return the decorated function unchanged."""
    def wrapper(func):
        return func
    return wrapper


def _get_track():
    """Return ``opik.track`` when available, else a no-op."""
    if not OPIK_ENABLED:
        return _noop_decorator
    try:
        from opik import track
        return track
    except ImportError:
        return _noop_decorator


def _update_current_span(**kwargs):
    """Best-effort update of the active Opik span (no-op if unavailable)."""
    if not OPIK_ENABLED:
        return
    try:
        from opik.opik_context import update_current_span
        update_current_span(**kwargs)
    except Exception:
        pass


def _update_current_trace(**kwargs):
    """Best-effort update of the active Opik trace (no-op if unavailable)."""
    if not OPIK_ENABLED:
        return
    try:
        from opik.opik_context import update_current_trace
        update_current_trace(**kwargs)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# RAG query tracking
# ---------------------------------------------------------------------------

def track_rag_query(name: Optional[str] = None):
    """
    Decorator that wraps a RAG / semantic-search function with Opik tracing.

    The first positional arg (or ``query`` kwarg) is captured as the query text.
    Result metadata (num results, content preview) is logged automatically.

    Usage::

        @track_rag_query(name="semantic_search")
        def semantic_search(query: str, k: int = 5):
            ...
    """
    if not OPIK_ENABLED:
        return lambda func: func

    _track = _get_track()

    def decorator(func):
        span_name = name or f"rag_{func.__name__}"

        @_track(name=span_name, tags=["rag", "search"])
        @wraps(func)
        def wrapper(*args, **kwargs):
            query_text = kwargs.get("query") or (args[0] if args else "unknown")
            k_val = kwargs.get("k", 5)

            _update_current_span(
                metadata={
                    "query": str(query_text)[:500],
                    "k": k_val,
                    "function": func.__name__,
                    "module": func.__module__,
                },
            )

            result = func(*args, **kwargs)

            # Annotate the span with result summary
            if isinstance(result, list):
                previews = []
                for doc in result[:3]:
                    content = (
                        doc.page_content[:200]
                        if hasattr(doc, "page_content")
                        else str(doc)[:200]
                    )
                    meta = doc.metadata if hasattr(doc, "metadata") else {}
                    previews.append({"content": content, "metadata": meta})

                _update_current_span(
                    metadata={
                        "num_results": len(result),
                        "results_preview": previews,
                        "success": True,
                    },
                )
            return result

        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Agent action tracking
# ---------------------------------------------------------------------------

def track_agent_action(agent_name: str, action_type: str):
    """
    Decorator that wraps an agentic AI phase / tool call with Opik tracing.

    Usage::

        @track_agent_action(agent_name="PreCallAgent", action_type="plan")
        def plan_pre_call_context(deal_id: int):
            ...
    """
    if not OPIK_ENABLED:
        return lambda func: func

    _track = _get_track()

    def decorator(func):
        span_name = f"agent_{agent_name}_{action_type}"

        @_track(name=span_name, tags=["agent", agent_name, action_type])
        @wraps(func)
        def wrapper(*args, **kwargs):
            safe_kwargs = {
                k: v for k, v in kwargs.items() if not callable(v)
            }
            _update_current_span(
                metadata={
                    "agent_name": agent_name,
                    "action_type": action_type,
                    "function": func.__name__,
                    "kwargs": safe_kwargs,
                },
            )

            result = func(*args, **kwargs)

            _update_current_span(
                metadata={
                    "success": True,
                    "result_type": type(result).__name__,
                },
            )
            return result

        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# API endpoint tracking
# ---------------------------------------------------------------------------

def track_api_endpoint(endpoint_name: str):
    """
    Decorator that wraps a FastAPI endpoint with Opik tracing.

    Usage::

        @app.post("/api/query")
        @track_api_endpoint("query_rag")
        def query_rag(request: QueryRequest):
            ...
    """
    if not OPIK_ENABLED:
        return lambda func: func

    _track = _get_track()

    def decorator(func):
        span_name = f"api_{endpoint_name}"

        @_track(name=span_name, tags=["api", endpoint_name])
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract Pydantic request body
            request_data: Dict[str, Any] = {}
            for arg in args:
                if hasattr(arg, "dict"):
                    try:
                        request_data = arg.dict()
                    except Exception:
                        pass
                    break

            _update_current_span(
                metadata={
                    "endpoint": endpoint_name,
                    "request": request_data,
                    "function": func.__name__,
                },
            )

            result = func(*args, **kwargs)

            _update_current_span(metadata={"success": True})
            return result

        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Custom event logging
# ---------------------------------------------------------------------------

def log_event(
    event_name: str,
    event_data: Dict[str, Any],
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log an ad-hoc event to Opik as a single-span trace.

    Useful for recording one-off milestones like "vector_store_rebuilt",
    "model_version_switched", etc.
    """
    if not OPIK_ENABLED:
        return

    client = get_opik_client()
    if client is None:
        return

    try:
        trace = client.trace(
            name=f"event:{event_name}",
            input=event_data,
            output={"logged": True},
            tags=tags or ["event"],
            metadata=metadata or {},
        )
        trace.end()
        logger.info(f"Logged Opik event: {event_name}")
    except Exception as exc:
        logger.debug(f"Failed to log event {event_name}: {exc}")


# ---------------------------------------------------------------------------
# OpenAI automatic tracking
# ---------------------------------------------------------------------------

def setup_openai_tracking() -> None:
    """
    Patch the OpenAI / Azure OpenAI client so that every chat-completion
    call is automatically traced.  Call once at application startup.
    """
    if not OPIK_ENABLED:
        return
    try:
        from opik.integrations.openai import track_openai
        track_openai()
        logger.info("OpenAI automatic tracking enabled via Opik")
    except Exception as exc:
        logger.debug(f"Could not setup OpenAI tracking: {exc}")


# ---------------------------------------------------------------------------
# Manual trace context manager
# ---------------------------------------------------------------------------

class OpikTrace:
    """
    Context manager for creating a manual Opik trace with intermediate steps.

    Usage::

        with OpikTrace("deal_creation", input_data={"deal_id": 123}) as t:
            similar = fetch_similar_deals(deal_id)
            t.log_step("fetch_similar_deals", {"count": len(similar)})

            points = generate_talking_points(deal_id)
            t.log_step("generate_talking_points", {"points": points})
    """

    def __init__(
        self,
        trace_name: str,
        input_data: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ):
        self.trace_name = trace_name
        self.input_data = input_data or {}
        self.tags = tags or []
        self._trace = None
        self._steps: List[Dict[str, Any]] = []
        self._enabled = OPIK_ENABLED

    def __enter__(self):
        if not self._enabled:
            return self

        client = get_opik_client()
        if client is None:
            self._enabled = False
            return self

        try:
            self._trace = client.trace(
                name=self.trace_name,
                input=self.input_data,
                tags=self.tags or [self.trace_name],
            )
        except Exception as exc:
            logger.debug(f"Could not create Opik trace: {exc}")
            self._enabled = False

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._enabled or self._trace is None:
            return

        try:
            output: Dict[str, Any] = {"steps": self._steps}
            meta: Dict[str, Any] = {"num_steps": len(self._steps)}

            if exc_type:
                output["error"] = str(exc_val)
                meta["success"] = False
            else:
                meta["success"] = True

            self._trace.update(output=output, metadata=meta)
            self._trace.end()
        except Exception as exc:
            logger.debug(f"Could not finalize Opik trace: {exc}")

    def log_step(
        self,
        step_name: str,
        step_data: Dict[str, Any],
        tags: Optional[List[str]] = None,
    ) -> None:
        """Record an intermediate step as a child span."""
        self._steps.append({"name": step_name, **step_data})

        if not self._enabled or self._trace is None:
            return

        try:
            span = self._trace.span(
                name=step_name,
                input=step_data,
                tags=tags or [],
            )
            span.end()
        except Exception as exc:
            logger.debug(f"Could not log step {step_name}: {exc}")

    def set_output(self, output: Dict[str, Any]) -> None:
        """Set the final output on the trace before exiting."""
        if not self._enabled or self._trace is None:
            return
        try:
            self._trace.update(output=output)
        except Exception:
            pass
