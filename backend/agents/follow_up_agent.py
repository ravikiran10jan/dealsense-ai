"""
Follow-Up Orchestration Agent (Post-Call Agent)

After a call ends, this agent autonomously:
 1. Generates Minutes of Meeting (MoM) from the transcript
 2. Extracts action items with owners and due dates
 3. Checks for missing critical deal info (budget, decision-maker, timeline)
 4. Runs risk detection on the transcript
 5. Updates deal health score with reasoning
 6. Produces a consolidated post-call report

This is the most "agentic" piece: it plans multiple sub-tasks, executes them,
reflects on completeness, and returns a structured report with citations.
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


# BANT criteria the agent checks for completeness
BANT_CRITERIA = {
    "budget": {
        "label": "Budget",
        "description": "Was the customer's budget or spending authority discussed?",
    },
    "authority": {
        "label": "Decision-Maker / Authority",
        "description": "Was the final decision-maker identified or present?",
    },
    "need": {
        "label": "Need / Pain Point",
        "description": "Were specific customer needs or pain points articulated?",
    },
    "timeline": {
        "label": "Timeline",
        "description": "Was a project timeline or decision timeline discussed?",
    },
}


class FollowUpOrchestrationAgent(BaseAgent):
    """
    Autonomous post-call agent.

    Agent Loop:
        PERCEPTION  -> Parse transcript, call metadata, existing deal context
        PLANNING    -> Decide sub-tasks: MoM, action items, BANT gap check,
                       risk scan, deal health update
        EXECUTION   -> Run each sub-task (LLM calls + RiskDetectionAgent)
        REFLECTION  -> Validate: are all sections complete? Any critical gaps?
        ACTION      -> Return consolidated post-call report
    """

    name = "FollowUpOrchestrationAgent"

    # ------------------------------------------------------------------
    # Phase 1 — PERCEPTION
    # ------------------------------------------------------------------
    async def perceive(self, request: Dict[str, Any]) -> Dict[str, Any]:
        transcript = request.get("transcript", "")
        self._transcript = transcript
        self._account_name = request.get("account_name", "Unknown")
        self._industry = request.get("industry", "")
        self._deal_stage = request.get("deal_stage", "Unknown")

        context = {
            "transcript": transcript,
            "transcript_length": len(transcript),
            "deal_id": request.get("deal_id"),
            "account_name": self._account_name,
            "industry": self._industry,
            "deal_stage": self._deal_stage,
            "contact_name": request.get("contact_name", ""),
            "seller_name": request.get("seller_name", "Seller"),
            "call_duration_minutes": request.get("call_duration_minutes", 0),
        }
        self._record_step(
            AgentPhase.PERCEPTION,
            f"Received post-call transcript ({len(transcript)} chars) for {self._account_name}",
        )
        return context

    # ------------------------------------------------------------------
    # Phase 2 — PLANNING
    # ------------------------------------------------------------------
    async def plan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        tools = [
            {
                "tool": "generate_mom",
                "purpose": "Generate Minutes of Meeting from transcript",
            },
            {
                "tool": "extract_action_items",
                "purpose": "Extract action items with owners and due dates",
            },
            {
                "tool": "bant_gap_check",
                "purpose": "Check for missing BANT criteria (Budget, Authority, Need, Timeline)",
            },
            {
                "tool": "risk_detection",
                "purpose": "Detect deal risks from transcript",
            },
            {
                "tool": "deal_health_assessment",
                "purpose": "Produce updated deal health score with reasoning",
            },
        ]

        # Skip LLM-heavy tasks if transcript is too short
        if context["transcript_length"] < 100:
            tools = [t for t in tools if t["tool"] in ("generate_mom", "bant_gap_check")]
            self._record_step(
                AgentPhase.PLANNING,
                "Transcript too short — reduced plan to MoM + BANT check only",
            )

        self._record_step(
            AgentPhase.PLANNING,
            f"Planned {len(tools)} sub-tasks: {', '.join(t['tool'] for t in tools)}",
        )
        return tools

    # ------------------------------------------------------------------
    # Phase 3 — TOOL EXECUTION
    # ------------------------------------------------------------------
    async def execute_tools(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        transcript = self._transcript
        context = {
            "account_name": self._account_name,
            "industry": self._industry,
            "deal_stage": self._deal_stage,
        }

        for step in plan:
            tool = step["tool"]
            try:
                if tool == "generate_mom":
                    results["mom"] = await self._generate_mom(transcript)
                elif tool == "extract_action_items":
                    results["action_items"] = await self._extract_action_items(transcript)
                elif tool == "bant_gap_check":
                    results["bant_analysis"] = await self._bant_gap_check(transcript)
                elif tool == "risk_detection":
                    results["risks"] = await self._run_risk_detection(transcript, context)
                elif tool == "deal_health_assessment":
                    results["deal_health"] = await self._assess_deal_health(
                        transcript, results
                    )

                self._record_step(
                    AgentPhase.TOOL_EXECUTION,
                    f"Executed {tool} successfully",
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
        gaps: List[str] = []
        confidence = 1.0

        # Check MoM
        mom = tool_results.get("mom", {})
        if not mom or mom.get("error"):
            gaps.append("Minutes of Meeting generation failed")
            confidence -= 0.2

        # Check action items
        action_items = tool_results.get("action_items", [])
        if not action_items:
            gaps.append("No action items extracted — verify manually")
            confidence -= 0.1

        # Check BANT completeness
        bant = tool_results.get("bant_analysis", {})
        missing_bant = [
            criteria["label"]
            for key, criteria in BANT_CRITERIA.items()
            if not bant.get(key, {}).get("discussed", False)
        ]
        if missing_bant:
            gaps.append(f"Missing BANT criteria: {', '.join(missing_bant)}")
            confidence -= 0.05 * len(missing_bant)

        # Check risk detection
        risks = tool_results.get("risks", {})
        if isinstance(risks, dict) and risks.get("error"):
            gaps.append("Risk detection failed — manual review recommended")
            confidence -= 0.1

        # Check deal health
        deal_health = tool_results.get("deal_health", {})
        if not deal_health or deal_health.get("error"):
            gaps.append("Deal health assessment failed")
            confidence -= 0.1

        confidence = max(0.2, confidence)
        confidence_label = (
            "high" if confidence >= 0.8
            else "medium" if confidence >= 0.5
            else "low"
        )

        reflection = {
            "is_complete": len(gaps) == 0,
            "gaps": gaps,
            "missing_bant": missing_bant,
            "confidence": round(confidence, 2),
            "confidence_label": confidence_label,
        }
        self._record_step(
            AgentPhase.REFLECTION,
            f"Confidence={confidence:.0%}, gaps={len(gaps)}, missing BANT={len(missing_bant)}",
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
        mom = tool_results.get("mom", {})
        action_items = tool_results.get("action_items", [])
        bant = tool_results.get("bant_analysis", {})
        risks = tool_results.get("risks", {})
        deal_health = tool_results.get("deal_health", {})

        # Build risk summary from either dict or list
        risk_list = []
        overall_risk = "none"
        if isinstance(risks, dict) and not risks.get("error"):
            risk_list = risks.get("risks", [])
            overall_risk = risks.get("overall_risk_level", "none")
        elif isinstance(risks, list):
            risk_list = risks
            high_count = sum(1 for r in risk_list if r.get("severity") == "high")
            overall_risk = "high" if high_count >= 1 else ("medium" if risk_list else "none")

        output = {
            "account_name": context["account_name"],
            "deal_stage": context["deal_stage"],
            "minutes_of_meeting": mom,
            "action_items": action_items,
            "bant_analysis": bant,
            "missing_bant_criteria": reflection.get("missing_bant", []),
            "risks": {
                "overall_risk_level": overall_risk,
                "details": risk_list,
            },
            "deal_health": deal_health,
            "post_call_gaps": reflection["gaps"],
            "confidence": reflection["confidence_label"],
        }

        # Build follow-up actions
        follow_up_actions = []

        # Flag missing BANT
        missing_bant = reflection.get("missing_bant", [])
        if missing_bant:
            follow_up_actions.append({
                "type": "bant_follow_up",
                "message": f"Missing critical deal info: {', '.join(missing_bant)}. "
                           "Schedule a follow-up to address these.",
                "priority": "high",
            })

        # Flag high risks
        if overall_risk in ("critical", "high"):
            follow_up_actions.append({
                "type": "risk_escalation",
                "message": f"Deal risk level is {overall_risk} — manager review recommended.",
                "priority": "high",
            })

        # Flag if deal health is low
        if isinstance(deal_health, dict) and deal_health.get("score", 10) <= 4:
            follow_up_actions.append({
                "type": "deal_health_alert",
                "message": f"Deal health score is {deal_health.get('score')}/10: "
                           f"{deal_health.get('reason', 'Review needed')}",
                "priority": "high",
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

    async def _generate_mom(self, transcript: str) -> Dict[str, Any]:
        """Generate structured Minutes of Meeting using LLM."""
        llm = _get_llm()
        prompt = f"""You are generating Minutes of Meeting (MoM) from a sales call transcript.

TRANSCRIPT:
{transcript[:12000]}

Generate a structured MoM with:
1. executive_summary: 2-3 sentence overview of the call
2. attendees_mentioned: list of names/roles mentioned
3. topics_discussed: list of key topics with brief descriptions
4. decisions_made: list of any decisions reached
5. open_items: list of unresolved topics
6. next_meeting: any mention of scheduling a follow-up

FORMAT AS JSON:
{{
    "executive_summary": "string",
    "attendees_mentioned": ["string"],
    "topics_discussed": [
        {{"topic": "string", "summary": "string"}}
    ],
    "decisions_made": ["string"],
    "open_items": ["string"],
    "next_meeting": "string or null"
}}

Return ONLY valid JSON."""

        try:
            callbacks = _get_llm_callbacks()
            config = {"callbacks": callbacks} if callbacks else {}
            response = llm.invoke(prompt, config=config) if config else llm.invoke(prompt)
            text = response.content.strip()
            text = self._extract_json(text)
            return json.loads(text)
        except Exception as exc:
            logger.warning(f"MoM generation failed: {exc}")
            return {
                "executive_summary": "MoM generation failed — manual review needed.",
                "attendees_mentioned": [],
                "topics_discussed": [],
                "decisions_made": [],
                "open_items": [],
                "next_meeting": None,
                "error": str(exc),
            }

    async def _extract_action_items(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract action items using the existing summarization module."""
        try:
            from summarization.action_items_extractor import extract_action_items
            return await extract_action_items(transcript=transcript)
        except Exception as exc:
            logger.warning(f"Action item extraction failed: {exc}")
            return []

    async def _bant_gap_check(self, transcript: str) -> Dict[str, Any]:
        """Use LLM to check which BANT criteria were covered in the call."""
        llm = _get_llm()

        criteria_descriptions = "\n".join(
            f"- {key}: {info['description']}"
            for key, info in BANT_CRITERIA.items()
        )

        prompt = f"""Analyze this sales call transcript and determine which of the following
deal qualification criteria (BANT) were discussed.

CRITERIA TO CHECK:
{criteria_descriptions}

TRANSCRIPT:
{transcript[:10000]}

For each criterion, indicate:
- discussed: true/false
- evidence: brief quote or paraphrase from the transcript (or "Not discussed" if absent)
- status: "covered" | "partially_covered" | "not_covered"

FORMAT AS JSON:
{{
    "budget": {{"discussed": bool, "evidence": "string", "status": "string"}},
    "authority": {{"discussed": bool, "evidence": "string", "status": "string"}},
    "need": {{"discussed": bool, "evidence": "string", "status": "string"}},
    "timeline": {{"discussed": bool, "evidence": "string", "status": "string"}}
}}

Return ONLY valid JSON."""

        try:
            callbacks = _get_llm_callbacks()
            config = {"callbacks": callbacks} if callbacks else {}
            response = llm.invoke(prompt, config=config) if config else llm.invoke(prompt)
            text = response.content.strip()
            text = self._extract_json(text)
            return json.loads(text)
        except Exception as exc:
            logger.warning(f"BANT gap check failed: {exc}")
            return {
                key: {"discussed": False, "evidence": "Analysis failed", "status": "unknown"}
                for key in BANT_CRITERIA
            }

    async def _run_risk_detection(
        self, transcript: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Delegate to RiskDetectionAgent for comprehensive risk analysis."""
        try:
            from .risk_detection_agent import RiskDetectionAgent

            risk_agent = RiskDetectionAgent()
            result = await risk_agent.run({
                "transcript": transcript,
                "account_name": context.get("account_name", "Unknown"),
                "deal_stage": context.get("deal_stage", "Unknown"),
                "industry": context.get("industry", ""),
            })
            return result.output if result.success else {"error": "Risk agent failed"}
        except Exception as exc:
            logger.warning(f"Risk detection delegation failed: {exc}")
            return {"error": str(exc)}

    async def _assess_deal_health(
        self, transcript: str, prior_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Produce a deal health score informed by MoM, action items, BANT, and risks."""
        llm = _get_llm()

        # Summarize prior results for the LLM
        mom_summary = ""
        mom = prior_results.get("mom", {})
        if isinstance(mom, dict) and not mom.get("error"):
            mom_summary = mom.get("executive_summary", "")

        action_count = len(prior_results.get("action_items", []))

        bant = prior_results.get("bant_analysis", {})
        bant_covered = sum(
            1 for v in bant.values()
            if isinstance(v, dict) and v.get("discussed")
        )
        bant_total = len(BANT_CRITERIA)

        risks = prior_results.get("risks", {})
        risk_summary = ""
        if isinstance(risks, dict) and not risks.get("error"):
            risk_details = risks.get("risks", risks.get("details", []))
            if isinstance(risk_details, list):
                risk_summary = "; ".join(
                    r.get("signal", r.get("category", ""))[:100]
                    for r in risk_details[:5]
                )

        prompt = f"""You are a deal health analyst. Based on the following post-call analysis,
provide a deal health score from 1 to 10 and a brief reason.

CALL SUMMARY: {mom_summary}
ACTION ITEMS EXTRACTED: {action_count}
BANT CRITERIA COVERED: {bant_covered}/{bant_total}
RISKS DETECTED: {risk_summary if risk_summary else 'None'}

TRANSCRIPT EXCERPT:
{transcript[:5000]}

Scoring guide:
- 1-3: Deal at risk — critical gaps, high risks, disengaged customer
- 4-6: Moderate — some progress but notable gaps or risks
- 7-8: Healthy — good engagement, most criteria covered, manageable risks
- 9-10: Strong — all criteria covered, enthusiastic customer, clear next steps

FORMAT AS JSON:
{{
    "score": number,
    "reason": "string",
    "positive_signals": ["string"],
    "risk_factors": ["string"],
    "recommended_next_steps": ["string"]
}}

Return ONLY valid JSON."""

        try:
            callbacks = _get_llm_callbacks()
            config = {"callbacks": callbacks} if callbacks else {}
            response = llm.invoke(prompt, config=config) if config else llm.invoke(prompt)
            text = response.content.strip()
            text = self._extract_json(text)
            result = json.loads(text)
            result["score"] = min(10, max(1, int(result.get("score", 5))))
            return result
        except Exception as exc:
            logger.warning(f"Deal health assessment failed: {exc}")
            return {
                "score": 5,
                "reason": "Automated assessment failed — manual review recommended",
                "positive_signals": [],
                "risk_factors": [],
                "recommended_next_steps": ["Review call transcript manually"],
                "error": str(exc),
            }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from potentially markdown-wrapped LLM output."""
        if "```json" in text:
            text = text[text.index("```json") + 7:]
            text = text[:text.index("```")]
        elif "```" in text:
            text = text[text.index("```") + 3:]
            text = text[:text.index("```")]
        return text.strip()
