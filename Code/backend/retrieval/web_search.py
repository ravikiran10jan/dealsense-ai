import urllib.parse
import re
import time
import logging
import threading

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker pattern for web search.

    States:
      CLOSED   -- normal operation, requests go through
      OPEN     -- too many failures, requests are rejected instantly
      HALF_OPEN -- after cooldown, allow one probe request

    Transitions:
      CLOSED  -> OPEN       when failure_count >= failure_threshold
      OPEN    -> HALF_OPEN  when cooldown_seconds have elapsed
      HALF_OPEN -> CLOSED   on success
      HALF_OPEN -> OPEN     on failure (resets cooldown)
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._state = self.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        with self._lock:
            if self._state == self.OPEN:
                # Check if cooldown has elapsed -> move to HALF_OPEN
                if time.monotonic() - self._last_failure_time >= self.cooldown_seconds:
                    self._state = self.HALF_OPEN
                    logger.info("Circuit breaker: OPEN -> HALF_OPEN (cooldown elapsed)")
            return self._state

    def allow_request(self) -> bool:
        """Return True if a request should be attempted."""
        current = self.state
        return current in (self.CLOSED, self.HALF_OPEN)

    def record_success(self):
        """Record a successful call -- resets the breaker to CLOSED."""
        with self._lock:
            self._failure_count = 0
            if self._state != self.CLOSED:
                logger.info(f"Circuit breaker: {self._state} -> CLOSED (success)")
            self._state = self.CLOSED

    def record_failure(self):
        """Record a failed call -- may trip the breaker to OPEN."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            if self._failure_count >= self.failure_threshold:
                if self._state != self.OPEN:
                    logger.warning(
                        f"Circuit breaker: {self._state} -> OPEN "
                        f"(failures={self._failure_count}/{self.failure_threshold})"
                    )
                self._state = self.OPEN


# Module-level circuit breaker instance (shared across all web_search calls)
_web_search_breaker = CircuitBreaker(failure_threshold=3, cooldown_seconds=60)


def get_circuit_breaker() -> CircuitBreaker:
    """Expose breaker for status/monitoring endpoints."""
    return _web_search_breaker


def web_search(query, max_results=5, timeout_seconds=8.0):
    """
    Search the web using DuckDuckGo HTML interface.
    Uses proper SSL verification for security.
    Protected by a circuit breaker that trips after 3 consecutive failures
    and skips web search for 60 seconds before retrying.

    Args:
        query: Search query string.
        max_results: Max number of snippets.
        timeout_seconds: Hard timeout for each search attempt.

    Returns:
        Concatenated result snippets, or "" on failure.
    """
    # --- Circuit breaker gate ---
    if not _web_search_breaker.allow_request():
        logger.info(
            f"Web search skipped (circuit breaker {_web_search_breaker.state})"
        )
        return ""

    results = []

    # First try the ddgs package
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                body = r.get("body", "")
                if body:
                    results.append(body)

        if results:
            _web_search_breaker.record_success()
            return "\n".join(results)
    except Exception as e:
        logger.warning(f"DDGS search failed: {e}")

    # Fallback: Use httpx library with proper SSL verification
    try:
        import httpx

        search_url = (
            f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        )

        with httpx.Client(timeout=timeout_seconds, verify=True) as client:
            response = client.get(
                search_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                },
            )
            response.raise_for_status()

        html = response.text

        # Extract result snippets from HTML
        snippet_pattern = r'class="result__snippet"[^>]*>([^<]+)<'
        snippets = re.findall(snippet_pattern, html)

        for snippet in snippets[:max_results]:
            clean_snippet = snippet.strip()
            if clean_snippet and len(clean_snippet) > 20:
                results.append(clean_snippet)

        if results:
            _web_search_breaker.record_success()
            return "\n".join(results)

    except Exception as e:
        if "SSL" in str(e) or "certificate" in str(e).lower():
            logger.warning(f"SSL verification failed for web search: {e}")
        else:
            logger.warning(f"HTML search fallback failed: {e}")

    # Both paths failed -> record failure for circuit breaker
    _web_search_breaker.record_failure()
    return ""

