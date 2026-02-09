"""
Opik configuration and initialization for DealSense AI.

Supports both Opik Cloud (via API key) and self-hosted deployments.
Opik tracing is opt-in: set OPIK_ENABLED=true in your .env to activate.
"""
import os
import logging
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_opik_client = None
_opik_configured = False


def is_opik_enabled() -> bool:
    """Check whether Opik tracing is enabled via environment variable."""
    return os.getenv("OPIK_ENABLED", "false").lower() in ("true", "1", "yes")


def configure_opik() -> None:
    """
    Configure the Opik SDK once at application startup.

    Reads the following env vars:
        OPIK_ENABLED      - "true" to enable (default: "false")
        OPIK_API_KEY       - API key for Opik Cloud (optional for self-hosted)
        OPIK_WORKSPACE     - Workspace name on Opik Cloud
        OPIK_URL_OVERRIDE  - URL for self-hosted Opik (e.g. http://localhost:5173)
        OPIK_PROJECT_NAME  - Project name in Opik (default: "dealsense-ai")
    """
    global _opik_configured

    if not is_opik_enabled():
        logger.info("Opik tracing is disabled (set OPIK_ENABLED=true to enable)")
        return

    try:
        import opik

        api_key = os.getenv("OPIK_API_KEY")
        workspace = os.getenv("OPIK_WORKSPACE")
        url_override = os.getenv("OPIK_URL_OVERRIDE")

        kwargs = {}
        if api_key:
            kwargs["api_key"] = api_key
        if workspace:
            kwargs["workspace"] = workspace
        if url_override:
            kwargs["url"] = url_override
        else:
            # Default to local/self-hosted if no cloud key provided
            if not api_key:
                kwargs["use_local"] = True

        opik.configure(**kwargs)

        # Set default project name via environment for the SDK to pick up
        project = os.getenv("OPIK_PROJECT_NAME", "dealsense-ai")
        os.environ.setdefault("OPIK_PROJECT_NAME", project)

        _opik_configured = True
        logger.info(f"Opik tracing configured (project={project})")

    except Exception as exc:
        logger.warning(f"Failed to configure Opik: {exc}. Tracing will be disabled.")
        _opik_configured = False


def get_opik_client():
    """
    Return a lazily-initialised Opik client instance.

    Returns None when Opik is not enabled or not configured.
    """
    global _opik_client

    if not is_opik_enabled() or not _opik_configured:
        return None

    if _opik_client is None:
        try:
            import opik
            _opik_client = opik.Opik()
        except Exception as exc:
            logger.warning(f"Could not create Opik client: {exc}")
            return None

    return _opik_client


def get_opik_tracer():
    """
    Return an OpikTracer callback handler for LangChain integrations.

    Returns None when Opik is not enabled.
    """
    if not is_opik_enabled() or not _opik_configured:
        return None

    try:
        from opik.integrations.langchain import OpikTracer
        return OpikTracer(
            tags=["dealsense-ai"],
        )
    except Exception as exc:
        logger.warning(f"Could not create OpikTracer: {exc}")
        return None


def track_if_enabled():
    """
    Return the opik.track decorator when enabled, or a no-op passthrough
    decorator when disabled.  This lets call-sites unconditionally decorate
    functions without import-guarding.
    """
    if is_opik_enabled() and _opik_configured:
        try:
            from opik import track
            return track
        except ImportError:
            pass

    # Return identity decorator as fallback
    def _noop(fn=None, **kwargs):
        if fn is not None:
            return fn
        return lambda f: f

    return _noop
