"""
Risk Detection Agent

Scans a call transcript for red flags and surfaces proactive alerts:
 - Competitor mentions
 - Pricing pushback / budget concerns
 - No clear next step agreed
 - Stakeholder misalignment
 - Timeline slippage signals
 - Champion / sponsor absence

Operates on transcripts (post-call or real-time snippet).
"""
import json
import logging
import os
from typing import Any, Dict, List

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from .base_agent import AgentPhase, AgentResult, BaseAgent

load_dotenv()
logger = logging.getLogger(__name__)

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
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


# Keywords used during perception for fast rule-based pre-screening
COMPETITOR_KEYWORDS = [
    "competitor", "accenture", "infosys", "tcs", "wipro", "cognizant",
    "ibm", "capgemini", "deloitte", "kpmg", "ey ", "pwc",
    "alternative", "other vendor", "another provider", "shopping around",
]

PRICING_KEYWORDS = [
    "too expensive", "over budget", "budget concern", "cost reduction",
    "cheaper", "price", "discount", "rate card", "value for money",
    "cannot afford", "budget cut", "lower the price",
]

NO_NEXT_STEP_SIGNALS = [
    "we'll get back to you", "let us think about it", "not sure about next steps",
    "need to discuss internally", "no rush", "some point",
]

TIMELINE_RISK_KEYWORDS = [
    "delay", "push back", "postpone", "reschedule", "not a priority",
    "next quarter", "next year", "on hold", "freeze",
]


class RiskDetectionAgent(BaseAgent):
    """
    Autonomous agent that detects deal risks from call transcripts.

    Agent Loop:
        PERCEPTION  -> Parse transcript + deal metadata
        PLANNING    -> Choose detection strategies (rule-based + LLM)
        EXECUTION   -> Run keyword scan, then LLM deep analysis
        REFLECTION  -> Cross-check findings, deduplicate, score severity
        ACTION      -> Return risk alerts with severity and recommendations
    """

    name = "RiskDetectionAgent"

    # ------------------------------------------------------------------
    # Phase 1 — PERCEPTION
    # ------------------------------------------------------------------
    async def perceive(self, request: Dict[str, Any]) -> Dict[str, Any]:
        transcript = request.get("transcript", "")
        self._transcript = transcript
        self._account_name = request.get("account_name", "Unknown")
        self._deal_stage = request.get("deal_stage", "Unknown")
        self._industry = request.get("industry", "")

        context = {
            "transcript": transcript,
            "transcript_length": len(transcript),
            "account_name": self._account_name,
            "deal_id": request.get("deal_id"),
            "deal_stage": self._deal_stage,
            "industry": self._industry,
        }
        self._record_step(
            AgentPhase.PERCEPTION,
            f"Received transcript ({len(transcript)} chars) for {self._account_name}",
        )
        return context

    # ------------------------------------------------------------------
    # Phase 2 — PLANNING
    # ------------------------------------------------------------------
    async def plan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        tools = [
            {
                "tool": "keyword_scan",
                "purpose": "Fast rule-based risk keyword detection",
            },
        ]
        # Only invoke LLM deep analysis for transcripts of meaningful length
        if context["transcript_length"] >= 100:
            tools.append({
                "tool": "llm_risk_analysis",
                "purpose": "Deep LLM-based risk detection with reasoning",
            })
        else:
            self._record_step(
                AgentPhase.PLANNING,
                "Transcript too short for LLM analysis — keyword scan only",
            )

        self._record_step(
            AgentPhase.PLANNING,
            f"Planned {len(tools)} tool(s): {', '.join(t['tool'] for t in tools)}",
        )
        return tools

    # ------------------------------------------------------------------
    # Phase 3 — TOOL EXECUTION
    # ------------------------------------------------------------------
    async def execute_tools(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        transcript = self._transcript
        account_name = self._account_name
        deal_stage = self._deal_stage
        industry = self._industry

        for step in plan:
            tool = step["tool"]
            try:
                if tool == "keyword_scan":
                    results["keyword_risks"] = self._keyword_scan(transcript)
                    self._record_step(
                        AgentPhase.TOOL_EXECUTION,
                        f"Keyword scan found {len(results['keyword_risks'])} signal(s)",
                        tool_name=tool,
                    )
                elif tool == "llm_risk_analysis":
                    results["llm_risks"] = await self._llm_risk_analysis(
                        transcript, account_name, deal_stage, industry
                    )
                    self._record_step(
                        AgentPhase.TOOL_EXECUTION,
                        f"LLM analysis found {len(results['llm_risks'])} risk(s)",
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
        keyword_risks = tool_results.get("keyword_risks", [])
        llm_risks = tool_results.get("llm_risks", [])

        # Merge and deduplicate
        all_risks = self._merge_risks(keyword_risks, llm_risks)

        # Assess overall deal risk level
        high_count = sum(1 for r in all_risks if r.get("severity") == "high")
        med_count = sum(1 for r in all_risks if r.get("severity") == "medium")

        if high_count >= 2:
            overall_risk = "critical"
        elif high_count >= 1 or med_count >= 3:
            overall_risk = "high"
        elif med_count >= 1:
            overall_risk = "medium"
        elif all_risks:
            overall_risk = "low"
        else:
            overall_risk = "none"

        confidence = 0.9 if llm_risks else 0.6  # LLM adds confidence

        reflection = {
            "merged_risks": all_risks,
            "overall_risk_level": overall_risk,
            "total_risks": len(all_risks),
            "confidence": confidence,
        }
        self._record_step(
            AgentPhase.REFLECTION,
            f"Overall risk={overall_risk}, {len(all_risks)} risk(s), confidence={confidence:.0%}",
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
        risks = reflection["merged_risks"]
        overall = reflection["overall_risk_level"]

        output = {
            "account_name": context["account_name"],
            "deal_stage": context["deal_stage"],
            "overall_risk_level": overall,
            "risks": risks,
            "total_risks_detected": len(risks),
        }

        # Determine follow-up actions
        follow_up_actions = []
        if overall in ("critical", "high"):
            follow_up_actions.append({
                "type": "escalation_alert",
                "message": f"Deal with {context['account_name']} has {overall} risk — "
                           "manager review recommended.",
                "severity": overall,
            })
        for risk in risks:
            if risk.get("severity") == "high" and risk.get("recommendation"):
                follow_up_actions.append({
                    "type": "action_item",
                    "message": risk["recommendation"],
                    "risk_category": risk["category"],
                })

        return AgentResult(
            success=True,
            output=output,
            confidence=reflection["confidence"],
            needs_follow_up=bool(follow_up_actions),
            follow_up_actions=follow_up_actions,
        )

    # ==================================================================
    # Private tool implementations
    # ==================================================================
    def _keyword_scan(self, transcript: str) -> List[Dict[str, Any]]:
        """Fast rule-based keyword scanning."""
        transcript_lower = transcript.lower()
        risks = []

        # Competitor mentions
        for kw in COMPETITOR_KEYWORDS:
            if kw in transcript_lower:
                risks.append({
                    "category": "competitor_mention",
                    "severity": "high",
                    "signal": f"Detected competitor-related keyword: '{kw}'",
                    "recommendation": "Prepare competitive differentiation points.",
                    "source": "keyword_scan",
                })
                break  # one signal per category for keywords

        # Pricing pushback
        for kw in PRICING_KEYWORDS:
            if kw in transcript_lower:
                risks.append({
                    "category": "pricing_pushback",
                    "severity": "high",
                    "signal": f"Detected pricing concern keyword: '{kw}'",
                    "recommendation": "Revisit value proposition; prepare ROI justification.",
                    "source": "keyword_scan",
                })
                break

        # No next step
        for kw in NO_NEXT_STEP_SIGNALS:
            if kw in transcript_lower:
                risks.append({
                    "category": "no_next_step",
                    "severity": "medium",
                    "signal": f"Detected stalling signal: '{kw}'",
                    "recommendation": "Proactively propose a concrete next step with a date.",
                    "source": "keyword_scan",
                })
                break

        # Timeline risk
        for kw in TIMELINE_RISK_KEYWORDS:
            if kw in transcript_lower:
                risks.append({
                    "category": "timeline_risk",
                    "severity": "medium",
                    "signal": f"Detected timeline risk keyword: '{kw}'",
                    "recommendation": "Confirm current timeline expectations with the buyer.",
                    "source": "keyword_scan",
                })
                break

        return risks

    async def _llm_risk_analysis(
        self, transcript: str, account_name: str, deal_stage: str, industry: str
    ) -> List[Dict[str, Any]]:
        """Deep LLM-based risk analysis."""
        llm = _get_llm()
        prompt = f"""You are a deal risk analyst for enterprise B2B sales.

CALL TRANSCRIPT (with {account_name}, stage: {deal_stage}, industry: {industry}):
{transcript[:12000]}

Analyze the transcript for deal risks. Look for:
1. **Competitor mentions** — any reference to alternative vendors
2. **Pricing/budget pushback** — cost objections, budget constraints
3. **No clear next step** — call ended without a concrete follow-up
4. **Stakeholder misalignment** — conflicting opinions among customer participants
5. **Champion absence** — the internal champion/sponsor was not present or engaged
6. **Timeline slippage** — signs the project timeline is at risk
7. **Scope creep signals** — customer expanding requirements without budget discussion

For each risk found, provide:
- category (one of: competitor_mention, pricing_pushback, no_next_step, stakeholder_misalignment, champion_absence, timeline_risk, scope_creep)
- severity (low, medium, high)
- signal (the specific evidence from the transcript)
- recommendation (what the seller should do)

If NO risks are detected, return an empty array.

FORMAT AS JSON array:
[
  {{
    "category": "string",
    "severity": "low|medium|high",
    "signal": "string",
    "recommendation": "string"
  }}
]

Return ONLY valid JSON."""

        try:
            callbacks = _get_llm_callbacks()
            config = {"callbacks": callbacks} if callbacks else {}
            response = llm.invoke(prompt, config=config) if config else llm.invoke(prompt)
            text = response.content.strip()
            if "```json" in text:
                text = text[text.index("```json") + 7:]
                text = text[:text.index("```")]
            elif "```" in text:
                text = text[text.index("```") + 3:]
                text = text[:text.index("```")]
            risks = json.loads(text.strip())
            for r in risks:
                r["source"] = "llm_analysis"
            return risks
        except Exception as exc:
            logger.warning(f"LLM risk analysis failed: {exc}")
            return []

    def _merge_risks(
        self,
        keyword_risks: List[Dict],
        llm_risks: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Merge keyword and LLM risks, preferring LLM detail when both find same category."""
        merged = {}

        # LLM risks take priority (more detailed)
        for risk in llm_risks:
            cat = risk.get("category", "unknown")
            if cat not in merged:
                merged[cat] = risk
            else:
                # Keep the higher severity
                if self._severity_rank(risk.get("severity")) > self._severity_rank(
                    merged[cat].get("severity")
                ):
                    merged[cat] = risk

        # Add keyword risks if category not covered, or upgrade severity if higher
        for risk in keyword_risks:
            cat = risk.get("category", "unknown")
            if cat not in merged:
                merged[cat] = risk
            elif self._severity_rank(risk.get("severity")) > self._severity_rank(
                merged[cat].get("severity")
            ):
                # Keyword has higher severity — keep keyword signal but preserve
                # LLM recommendation if it exists (LLM recommendations are richer)
                llm_rec = merged[cat].get("recommendation")
                merged[cat] = risk
                if llm_rec:
                    merged[cat]["recommendation"] = llm_rec

        return list(merged.values())

    @staticmethod
    def _severity_rank(severity: str) -> int:
        return {"low": 1, "medium": 2, "high": 3}.get(severity, 0)
