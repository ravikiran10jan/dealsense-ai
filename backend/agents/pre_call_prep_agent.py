"""
Pre-Call Prep Agent

Given a deal, autonomously:
 1. Gathers similar deals and case studies from the vector DB
 2. Retrieves credible reference contacts
 3. Generates tailored talking points
 4. Anticipates expected questions from the customer
 5. Produces a consolidated pre-call brief
"""
import logging
import os
from typing import Any, Dict, List

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from .base_agent import AgentPhase, AgentResult, BaseAgent

load_dotenv()
logger = logging.getLogger(__name__)

# Lazy LLM singleton
_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    return _llm


def _get_llm_callbacks() -> list:
    """Return Opik tracer callback list if enabled, else empty."""
    try:
        from observability.opik_config import get_opik_tracer
        tracer = get_opik_tracer()
        if tracer:
            return [tracer]
    except Exception:
        pass
    return []


class PreCallPrepAgent(BaseAgent):
    """
    Autonomous agent that prepares a seller for an upcoming call.

    Agent Loop:
        PERCEPTION  -> Extract deal_id, account, industry, description
        PLANNING    -> Determine which tools are needed
        EXECUTION   -> RAG search (similar deals), reference lookup,
                       talking-points generation, question anticipation
        REFLECTION  -> Check coverage: do we have references? talking points?
                       Are there gaps the seller should know about?
        ACTION      -> Return structured pre-call brief
    """

    name = "PreCallPrepAgent"

    # ------------------------------------------------------------------
    # Phase 1 — PERCEPTION
    # ------------------------------------------------------------------
    async def perceive(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize deal context from the request."""
        context = {
            "deal_id": request.get("deal_id"),
            "account_name": request.get("account_name", "Unknown"),
            "industry": request.get("industry", ""),
            "description": request.get("description", ""),
            "deal_stage": request.get("deal_stage", "Discovery"),
            "deal_amount": request.get("deal_amount", ""),
            "contact_name": request.get("contact_name", ""),
            "contact_role": request.get("contact_role", ""),
        }
        self._record_step(
            AgentPhase.PERCEPTION,
            f"Parsed deal context for {context['account_name']}",
        )
        return context

    # ------------------------------------------------------------------
    # Phase 2 — PLANNING
    # ------------------------------------------------------------------
    async def plan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decide which tools to call."""
        tools = [
            {
                "tool": "semantic_search",
                "purpose": "Find similar deals and case studies",
                "query": f"Similar {context['industry']} implementations case studies "
                         f"for {context['description']} with team size timeline outcomes",
            },
            {
                "tool": "credible_references",
                "purpose": "Retrieve reference contacts",
                "params": {
                    "industry": context["industry"],
                    "description": context["description"],
                },
            },
            {
                "tool": "talking_points_llm",
                "purpose": "Generate tailored talking points",
                "params": {
                    "client_name": context["account_name"],
                    "industry": context["industry"],
                    "description": context["description"],
                },
            },
            {
                "tool": "expected_questions_llm",
                "purpose": "Anticipate customer questions",
                "params": {
                    "account_name": context["account_name"],
                    "industry": context["industry"],
                    "description": context["description"],
                    "contact_role": context["contact_role"],
                },
            },
        ]
        self._record_step(
            AgentPhase.PLANNING,
            f"Planned {len(tools)} tool calls: "
            + ", ".join(t["tool"] for t in tools),
        )
        return tools

    # ------------------------------------------------------------------
    # Phase 3 — TOOL EXECUTION
    # ------------------------------------------------------------------
    async def execute_tools(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute each planned tool call and collect results."""
        results: Dict[str, Any] = {}

        for step in plan:
            tool = step["tool"]
            try:
                if tool == "semantic_search":
                    results["similar_deals"] = self._run_semantic_search(step["query"])

                elif tool == "credible_references":
                    results["references"] = self._run_credible_references(step["params"])

                elif tool == "talking_points_llm":
                    results["talking_points"] = self._run_talking_points(step["params"])

                elif tool == "expected_questions_llm":
                    rag_context = results.get("similar_deals", {}).get("context", "")
                    results["expected_questions"] = await self._run_expected_questions(
                        step["params"], rag_context
                    )

                self._record_step(
                    AgentPhase.TOOL_EXECUTION,
                    f"Executed {tool}",
                    tool_name=tool,
                )
            except Exception as exc:
                logger.warning(f"[{self.name}] Tool {tool} failed: {exc}")
                results[tool] = {"error": str(exc)}
                self._record_step(
                    AgentPhase.TOOL_EXECUTION,
                    f"Tool {tool} FAILED: {exc}",
                    tool_name=tool,
                )

        return results

    # ------------------------------------------------------------------
    # Phase 4 — REFLECTION
    # ------------------------------------------------------------------
    async def reflect(
        self, context: Dict[str, Any], tool_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate completeness and assess confidence."""
        gaps: List[str] = []
        confidence = 1.0

        # Check similar deals
        similar = tool_results.get("similar_deals", {})
        if not similar.get("deals"):
            gaps.append("No similar deals found in knowledge base")
            confidence -= 0.2

        # Check references
        refs = tool_results.get("references", [])
        if not refs:
            gaps.append("No credible references found — consider manual lookup")
            confidence -= 0.15

        # Check talking points
        tp = tool_results.get("talking_points", {})
        if not tp.get("talking_points"):
            gaps.append("Talking points generation fell back to generic defaults")
            confidence -= 0.15

        # Check expected questions
        eq = tool_results.get("expected_questions", [])
        if not eq:
            gaps.append("Could not anticipate customer questions")
            confidence -= 0.1

        confidence = max(0.3, confidence)

        reflection = {
            "is_complete": len(gaps) == 0,
            "gaps": gaps,
            "confidence": round(confidence, 2),
        }

        self._record_step(
            AgentPhase.REFLECTION,
            f"Confidence={confidence:.0%}, gaps={len(gaps)}",
        )
        return reflection

    # ------------------------------------------------------------------
    # Phase 5 — ACTION
    # ------------------------------------------------------------------
    async def act(
        self,
        context: Dict[str, Any],
        tool_results: Dict[str, Any],
        reflection: Dict[str, Any],
    ) -> AgentResult:
        """Produce the consolidated pre-call brief."""
        similar = tool_results.get("similar_deals", {})
        refs = tool_results.get("references", [])
        tp = tool_results.get("talking_points", {})
        eq = tool_results.get("expected_questions", [])

        output = {
            "account_name": context["account_name"],
            "deal_stage": context["deal_stage"],
            "similar_deals": similar.get("deals", []),
            "credible_references": refs,
            "suggested_talking_points": tp.get("talking_points", []),
            "expected_questions": eq,
            "preparation_gaps": reflection["gaps"],
        }

        follow_up_actions = []
        if reflection["gaps"]:
            follow_up_actions.append({
                "type": "alert",
                "message": f"Pre-call prep has {len(reflection['gaps'])} gap(s) — review before the call.",
                "gaps": reflection["gaps"],
            })

        return AgentResult(
            success=True,
            output=output,
            confidence=reflection["confidence"],
            needs_follow_up=bool(follow_up_actions),
            follow_up_actions=follow_up_actions,
        )

    # ==================================================================
    # Private tool wrappers
    # ==================================================================
    def _run_semantic_search(self, query: str) -> Dict[str, Any]:
        from retrieval.semantic_search import semantic_search_with_scores

        results = semantic_search_with_scores(query, k=5)
        deals = []
        context_parts = []
        for doc, score in results:
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content[:500]
            deals.append({
                "source": source,
                "snippet": content[:200],
                "relevance_score": round(float(1.0 - min(float(score) / 2.0, 1.0)), 2),
            })
            context_parts.append(f"[{source}]: {content}")
        return {"deals": deals, "context": "\n\n".join(context_parts)}

    def _run_credible_references(self, params: Dict) -> List[Dict]:
        from llm.credible_references import get_credible_references

        return get_credible_references(
            industry=params.get("industry", ""),
            description=params.get("description", ""),
            max_references=3,
        )

    def _run_talking_points(self, params: Dict) -> Dict[str, Any]:
        from llm.talking_points import generate_talking_points_from_query
        from retrieval.semantic_search import semantic_search

        return generate_talking_points_from_query(
            client_name=params["client_name"],
            industry=params["industry"],
            description=params["description"],
            semantic_search_fn=semantic_search,
            num_points=4,
        )

    async def _run_expected_questions(
        self, params: Dict, rag_context: str
    ) -> List[Dict[str, Any]]:
        llm = _get_llm()
        prompt = f"""You are a sales strategy assistant. A seller is preparing for a call.

CLIENT CONTEXT:
- Account: {params['account_name']}
- Industry: {params['industry']}
- Deal Focus: {params['description']}
- Primary Contact Role: {params.get('contact_role', 'Unknown')}

RELEVANT KNOWLEDGE BASE CONTEXT:
{rag_context[:3000] if rag_context else 'No specific context available.'}

Generate 5-8 questions the customer is likely to ask during the call, grouped by theme.
For each question, provide a brief suggested response approach.

FORMAT AS JSON array of objects:
[
  {{
    "theme": "string",
    "question": "string",
    "suggested_approach": "string"
  }}
]

Return ONLY valid JSON."""

        try:
            import json
            callbacks = _get_llm_callbacks()
            config = {"callbacks": callbacks} if callbacks else {}
            response = llm.invoke(prompt, config=config) if config else llm.invoke(prompt)
            text = response.content.strip()
            # Extract JSON from potential markdown wrapping
            if "```json" in text:
                text = text[text.index("```json") + 7:]
                text = text[:text.index("```")]
            elif "```" in text:
                text = text[text.index("```") + 3:]
                text = text[:text.index("```")]
            return json.loads(text.strip())
        except Exception as exc:
            logger.warning(f"Expected questions LLM call failed: {exc}")
            return []
