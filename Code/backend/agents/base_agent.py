"""
Base Agent Framework for DealSense AI.

Implements the core Agentic AI loop:
    1. PERCEPTION  - Parse the incoming request, extract intent and context
    2. PLANNING    - Decide which tools to invoke and in what order
    3. TOOL EXECUTION - Call semantic_search, web_search, LLM, CRM lookup, etc.
    4. REFLECTION  - Validate completeness, check for hallucination, assess confidence
    5. ACTION      - Return the final answer or trigger a follow-up action

Every concrete agent subclasses BaseAgent and implements the five phases.
"""
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _get_opik_track():
    """Return opik.track when enabled, identity decorator otherwise."""
    try:
        from observability.opik_config import track_if_enabled
        return track_if_enabled()
    except Exception:
        return lambda fn=None, **kw: fn if fn else (lambda f: f)


class AgentPhase(str, Enum):
    PERCEPTION = "perception"
    PLANNING = "planning"
    TOOL_EXECUTION = "tool_execution"
    REFLECTION = "reflection"
    ACTION = "action"


@dataclass
class AgentStep:
    """A single step in the agent's execution trace."""
    phase: AgentPhase
    description: str
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Any] = None
    duration_ms: float = 0.0


@dataclass
class AgentResult:
    """Final output of an agent run."""
    success: bool
    output: Dict[str, Any]
    steps: List[AgentStep] = field(default_factory=list)
    confidence: float = 0.0
    needs_follow_up: bool = False
    follow_up_actions: List[Dict[str, Any]] = field(default_factory=list)
    total_duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "confidence": round(self.confidence, 2),
            "needs_follow_up": self.needs_follow_up,
            "follow_up_actions": self.follow_up_actions,
            "agent_trace": [
                {
                    "phase": step.phase.value,
                    "description": step.description,
                    "tool": step.tool_name,
                    "duration_ms": round(step.duration_ms, 1),
                }
                for step in self.steps
            ],
            "total_duration_ms": round(self.total_duration_ms, 1),
        }


class BaseAgent(ABC):
    """
    Abstract base class for all DealSense AI agents.

    Subclasses must implement the five agentic phases:
        perceive, plan, execute_tools, reflect, act
    """

    name: str = "BaseAgent"

    def __init__(self):
        self._steps: List[AgentStep] = []

    # ------------------------------------------------------------------
    # Agentic loop
    # ------------------------------------------------------------------
    async def run(self, request: Dict[str, Any]) -> AgentResult:
        """
        Execute the full agent loop:
        Perception -> Planning -> Tool Execution -> Reflection -> Action

        When Opik is enabled, the entire run is wrapped in a tracked span
        so that each agent invocation appears as a top-level trace.
        """
        self._steps = []
        loop_start = time.perf_counter()

        try:
            # 1. PERCEPTION
            context = await self._timed_phase(
                AgentPhase.PERCEPTION,
                "Parse query and call context",
                self.perceive,
                request,
            )

            # 2. PLANNING
            plan = await self._timed_phase(
                AgentPhase.PLANNING,
                "Decide which tools to call",
                self.plan,
                context,
            )

            # 3. TOOL EXECUTION
            tool_results = await self._timed_phase(
                AgentPhase.TOOL_EXECUTION,
                "Execute planned tool calls",
                self.execute_tools,
                plan,
            )

            # 4. REFLECTION
            reflection = await self._timed_phase(
                AgentPhase.REFLECTION,
                "Validate completeness and confidence",
                self.reflect,
                context,
                tool_results,
            )

            # 5. ACTION
            result = await self._timed_phase(
                AgentPhase.ACTION,
                "Produce final output or trigger follow-up",
                self.act,
                context,
                tool_results,
                reflection,
            )

            total_ms = (time.perf_counter() - loop_start) * 1000
            result.steps = self._steps
            result.total_duration_ms = total_ms

            # Log the agent run to Opik when enabled
            self._log_agent_trace_to_opik(request, result)

            return result

        except Exception as exc:
            total_ms = (time.perf_counter() - loop_start) * 1000
            logger.error(f"[{self.name}] Agent loop failed: {exc}", exc_info=True)
            return AgentResult(
                success=False,
                output={"error": str(exc)},
                steps=self._steps,
                total_duration_ms=total_ms,
            )

    # ------------------------------------------------------------------
    # Abstract phases — every agent must implement these
    # ------------------------------------------------------------------
    @abstractmethod
    async def perceive(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 1: Parse and understand the incoming request."""
        ...

    @abstractmethod
    async def plan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Phase 2: Decide which tools to call and in what order."""
        ...

    @abstractmethod
    async def execute_tools(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Phase 3: Execute each planned tool call and collect results."""
        ...

    @abstractmethod
    async def reflect(
        self, context: Dict[str, Any], tool_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 4: Validate results, check confidence, detect gaps."""
        ...

    @abstractmethod
    async def act(
        self,
        context: Dict[str, Any],
        tool_results: Dict[str, Any],
        reflection: Dict[str, Any],
    ) -> AgentResult:
        """Phase 5: Produce the final result or trigger follow-up actions."""
        ...

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _record_step(
        self,
        phase: AgentPhase,
        description: str,
        tool_name: Optional[str] = None,
        tool_input: Optional[Dict[str, Any]] = None,
        tool_output: Optional[Any] = None,
        duration_ms: float = 0.0,
    ) -> None:
        self._steps.append(
            AgentStep(
                phase=phase,
                description=description,
                tool_name=tool_name,
                tool_input=tool_input,
                tool_output=tool_output,
                duration_ms=duration_ms,
            )
        )

    async def _timed_phase(self, phase, description, fn, *args):
        """Run an agent phase, record its step with timing."""
        start = time.perf_counter()
        result = await fn(*args)
        elapsed = (time.perf_counter() - start) * 1000
        self._record_step(phase, description, duration_ms=elapsed)
        logger.info(f"[{self.name}] {phase.value}: {description} ({elapsed:.0f}ms)")
        return result

    def _log_agent_trace_to_opik(
        self, request: Dict[str, Any], result: "AgentResult"
    ) -> None:
        """Send the completed agent run as an Opik trace (best-effort)."""
        try:
            from observability.opik_config import is_opik_enabled, get_opik_client

            if not is_opik_enabled():
                return

            client = get_opik_client()
            if client is None:
                return

            # Log a trace for the full agent run
            trace = client.trace(
                name=f"agent:{self.name}",
                input=request,
                output=result.output,
                tags=["agent", self.name],
                metadata={
                    "agent_name": self.name,
                    "success": result.success,
                    "confidence": result.confidence,
                    "total_duration_ms": result.total_duration_ms,
                    "num_steps": len(result.steps),
                },
            )

            # Log each phase as a span under the trace
            for step in result.steps:
                trace.span(
                    name=f"{step.phase.value}:{step.description}",
                    input=step.tool_input or {},
                    output={"tool": step.tool_name} if step.tool_name else {},
                    metadata={"duration_ms": step.duration_ms},
                )

            trace.end()

        except Exception as exc:
            logger.debug(f"Could not log agent trace to Opik: {exc}")
