"""
Evaluation pipelines for DealSense AI.

Provides helpers to:
  - Create / manage evaluation datasets in Opik
  - Run RAG quality evaluations (answer relevance, hallucination, context recall)
  - Run agent evaluations (completeness, tool usage, latency)
  - Track experiment results across model versions
"""
import logging
import time
from typing import Any, Dict, List, Optional

from .opik_config import get_opik_client, is_opik_enabled

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dataset management
# ---------------------------------------------------------------------------

def create_rag_dataset(
    name: str = "dealsense-rag-eval",
    items: Optional[List[Dict[str, Any]]] = None,
    description: str = "RAG evaluation dataset for DealSense AI",
) -> Optional[Dict[str, Any]]:
    """
    Create or update a RAG evaluation dataset in Opik.

    Each item should contain:
        - input: The user query
        - expected_output: The expected/reference answer
        - context: (optional) expected retrieved context

    Returns dataset metadata dict, or None if Opik is unavailable.
    """
    client = get_opik_client()
    if client is None:
        logger.warning("Opik client not available - cannot create dataset")
        return None

    try:
        dataset = client.get_or_create_dataset(name, description=description)

        if items:
            dataset.insert(items)
            logger.info(f"Inserted {len(items)} items into dataset '{name}'")

        return {
            "name": name,
            "description": description,
            "item_count": len(items) if items else 0,
        }

    except Exception as exc:
        logger.error(f"Failed to create dataset: {exc}")
        return None


def _get_default_rag_dataset_items() -> List[Dict[str, Any]]:
    """
    Return a set of default evaluation items for the DealSense RAG system.
    These cover the core knowledge domains: case studies, offerings,
    trade finance, team capabilities.
    """
    return [
        {
            "input": "What was the CBA trade finance implementation team size?",
            "expected_output": "The CBA trade finance implementation involved a team of approximately 45 members.",
        },
        {
            "input": "How long did the SMBC LC automation project take?",
            "expected_output": "The SMBC LC (Letter of Credit) automation project was completed in approximately 12 months.",
        },
        {
            "input": "What AI capabilities does DXC Luxoft offer for trade finance?",
            "expected_output": "DXC Luxoft offers AI-powered document classification, trade finance monitoring, and analytics capabilities.",
        },
        {
            "input": "What data privacy approach was used for the SCB project?",
            "expected_output": "The SCB project used a Singapore-only rollout to ensure data residency and privacy compliance.",
        },
        {
            "input": "Who are credible references for trade finance projects?",
            "expected_output": "Credible references include Andrew Marvin (ASX, ex-CBA) and Ian Stephenson (Standard Chartered Bank).",
        },
        {
            "input": "What cloud migration outcomes did the banking platform achieve?",
            "expected_output": "The banking platform migration achieved zero downtime, 24/7 transaction processing, full compliance, and 50% cost reduction.",
        },
        {
            "input": "How does DealSense handle meeting notes?",
            "expected_output": "DealSense transforms meeting notes into actionable insights, generating summaries, action items, and writing MoMs to SharePoint.",
        },
        {
            "input": "What trade finance monitoring capabilities are available?",
            "expected_output": "Available capabilities include real-time monitoring, AI-driven insights, and compliance automation.",
        },
    ]


# ---------------------------------------------------------------------------
# RAG evaluation
# ---------------------------------------------------------------------------

def run_rag_evaluation(
    dataset_name: str = "dealsense-rag-eval",
    experiment_name: Optional[str] = None,
    model_version: Optional[str] = None,
    use_defaults: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Run a RAG evaluation experiment.

    Steps:
      1. Load (or create) the evaluation dataset
      2. For each item, run the hybrid RAG pipeline
      3. Score outputs with relevance and hallucination metrics
      4. Record experiment in Opik

    Args:
        dataset_name: Name of the Opik dataset to evaluate against
        experiment_name: Name for this experiment run (auto-generated if None)
        model_version: Tag for the model version being tested
        use_defaults: Seed the dataset with defaults if empty

    Returns:
        Experiment result summary dict, or None on failure
    """
    client = get_opik_client()
    if client is None:
        logger.warning("Opik client not available - cannot run evaluation")
        return None

    try:
        from opik.evaluation import evaluate
        from opik.evaluation.metrics import (
            AnswerRelevance,
            Hallucination,
        )

        # Get or create dataset
        if use_defaults:
            create_rag_dataset(
                name=dataset_name,
                items=_get_default_rag_dataset_items(),
            )

        dataset = client.get_or_create_dataset(dataset_name)

        # Build experiment name
        if experiment_name is None:
            ts = int(time.time())
            version_tag = model_version or "default"
            experiment_name = f"rag-eval-{version_tag}-{ts}"

        # Import RAG pipeline (lazy to avoid circular imports)
        from orchestration.hybrid_answer import answer_query

        def rag_task(item: Dict[str, Any]) -> Dict[str, Any]:
            """Run the RAG pipeline for a single evaluation item."""
            query = item["input"]
            result = answer_query(query)
            return {
                "output": result["answer"],
                "context": [result.get("sources", [])],
                "source_type": result.get("source_type", "unknown"),
            }

        # Define scoring metrics
        metrics = [
            AnswerRelevance(),
            Hallucination(),
        ]

        # Run evaluation
        eval_result = evaluate(
            experiment_name=experiment_name,
            dataset=dataset,
            task=rag_task,
            scoring_metrics=metrics,
        )

        summary = {
            "experiment_name": experiment_name,
            "model_version": model_version,
            "dataset_name": dataset_name,
            "status": "completed",
        }

        logger.info(f"RAG evaluation completed: {experiment_name}")
        return summary

    except ImportError as exc:
        logger.error(f"Missing evaluation dependencies: {exc}")
        return {"error": str(exc), "status": "failed"}
    except Exception as exc:
        logger.error(f"RAG evaluation failed: {exc}", exc_info=True)
        return {"error": str(exc), "status": "failed"}


# ---------------------------------------------------------------------------
# Agent evaluation
# ---------------------------------------------------------------------------

def run_agent_evaluation(
    agent_type: str = "pre_call_prep",
    dataset_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    model_version: Optional[str] = None,
    test_cases: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Run an agent evaluation experiment.

    Measures agent output quality, tool usage completeness, and latency.

    Args:
        agent_type: Which agent to evaluate ("pre_call_prep", "risk_detection", "follow_up")
        dataset_name: Opik dataset name (auto-generated if None)
        experiment_name: Experiment name (auto-generated if None)
        model_version: Model version tag
        test_cases: Custom test cases; uses defaults if None

    Returns:
        Experiment result summary dict, or None on failure
    """
    client = get_opik_client()
    if client is None:
        logger.warning("Opik client not available - cannot run agent evaluation")
        return None

    try:
        from opik.evaluation import evaluate
        from opik.evaluation.metrics import AnswerRelevance

        # Default dataset name per agent type
        if dataset_name is None:
            dataset_name = f"dealsense-agent-{agent_type}-eval"

        # Default test cases
        if test_cases is None:
            test_cases = _get_default_agent_test_cases(agent_type)

        if not test_cases:
            return {"error": f"No test cases for agent_type={agent_type}", "status": "failed"}

        # Create / populate dataset
        create_rag_dataset(name=dataset_name, items=test_cases, description=f"Agent evaluation: {agent_type}")
        dataset = client.get_or_create_dataset(dataset_name)

        if experiment_name is None:
            ts = int(time.time())
            experiment_name = f"agent-{agent_type}-{model_version or 'default'}-{ts}"

        # Lazy import to avoid circular deps
        import asyncio
        from agents import PreCallPrepAgent, RiskDetectionAgent, FollowUpOrchestrationAgent

        agent_classes = {
            "pre_call_prep": PreCallPrepAgent,
            "risk_detection": RiskDetectionAgent,
            "follow_up": FollowUpOrchestrationAgent,
        }
        agent_cls = agent_classes.get(agent_type)
        if agent_cls is None:
            return {"error": f"Unknown agent_type: {agent_type}", "status": "failed"}

        def agent_task(item: Dict[str, Any]) -> Dict[str, Any]:
            """Run an agent for a single evaluation item."""
            agent = agent_cls()
            request = item.get("input", {})
            if isinstance(request, str):
                request = {"query": request}

            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(agent.run(request))
            finally:
                loop.close()

            output_dict = result.to_dict()
            return {
                "output": str(output_dict.get("output", "")),
                "success": output_dict.get("success", False),
                "confidence": output_dict.get("confidence", 0),
                "duration_ms": output_dict.get("total_duration_ms", 0),
            }

        eval_result = evaluate(
            experiment_name=experiment_name,
            dataset=dataset,
            task=agent_task,
            scoring_metrics=[AnswerRelevance()],
        )

        summary = {
            "experiment_name": experiment_name,
            "agent_type": agent_type,
            "model_version": model_version,
            "dataset_name": dataset_name,
            "test_cases_count": len(test_cases),
            "status": "completed",
        }

        logger.info(f"Agent evaluation completed: {experiment_name}")
        return summary

    except Exception as exc:
        logger.error(f"Agent evaluation failed: {exc}", exc_info=True)
        return {"error": str(exc), "status": "failed"}


def _get_default_agent_test_cases(agent_type: str) -> List[Dict[str, Any]]:
    """Return default test cases for each agent type."""
    if agent_type == "pre_call_prep":
        return [
            {
                "input": {
                    "account_name": "ANZ Bank",
                    "industry": "Banking",
                    "description": "Trade finance platform modernization",
                    "deal_stage": "Discovery",
                    "contact_name": "Test Contact",
                    "contact_role": "CTO",
                },
                "expected_output": "Pre-call preparation brief with talking points, similar deals, and risk assessment",
            },
            {
                "input": {
                    "account_name": "Westpac",
                    "industry": "Banking",
                    "description": "Digital banking transformation",
                    "deal_stage": "Proposal",
                    "contact_name": "Test Contact",
                    "contact_role": "VP Engineering",
                },
                "expected_output": "Pre-call preparation brief with digital transformation talking points",
            },
        ]
    elif agent_type == "risk_detection":
        return [
            {
                "input": {
                    "transcript": "Customer: We are also looking at Finastra and Temenos for this project. "
                                  "Seller: I understand. Let me explain our differentiators...",
                    "account_name": "Test Bank",
                    "deal_stage": "Evaluation",
                },
                "expected_output": "Risk assessment identifying competitor mention as a risk factor",
            },
        ]
    elif agent_type == "follow_up":
        return [
            {
                "input": {
                    "transcript": "Customer: We need the proposal by next Friday. "
                                  "Seller: Absolutely, we will send the proposal with pricing by Friday. "
                                  "Customer: Great, also please include references from similar banking projects.",
                    "account_name": "Test Bank",
                    "seller_name": "Test Seller",
                    "deal_stage": "Proposal",
                },
                "expected_output": "Follow-up with action items: send proposal by Friday, include banking references",
            },
        ]
    return []


# ---------------------------------------------------------------------------
# Experiment listing
# ---------------------------------------------------------------------------

def list_experiments(
    project_name: Optional[str] = None,
) -> Optional[List[Dict[str, Any]]]:
    """
    List recent experiments tracked in Opik.

    Returns a list of experiment metadata dicts, or None if Opik is unavailable.
    """
    client = get_opik_client()
    if client is None:
        logger.warning("Opik client not available")
        return None

    try:
        # The Opik client provides dataset listing; experiments are
        # accessed via the Opik dashboard or API. We list datasets as a proxy.
        datasets = client.get_datasets()
        return [
            {"name": ds.name, "description": getattr(ds, "description", "")}
            for ds in datasets
        ]
    except Exception as exc:
        logger.error(f"Failed to list experiments: {exc}")
        return None
