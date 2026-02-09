#!/usr/bin/env python3
"""
DealSense AI - End-to-End Demo Script
========================================
Runs the complete 3-minute demo flow:

  1. Seller creates deal for "ANZ Bank - Trade Finance Platform"
  2. Pre-call agent populates context (similar deals, references, talking points)
  3. Mock transcript is fed in (ANZ discovery call)
  4. Push-to-talk query: "What was CBA's implementation timeline?"
  5. Post-call agent generates summary with deal health score
  6. Seller approves -> MoM written to SharePoint (mock)

Prerequisites:
  - Backend running: DEALSENSE_DEV_MODE=true uvicorn api:app --port 8000
  - Or: set DEALSENSE_DEV_MODE=true in .env and run normally

Usage:
  python demo_e2e.py [--base-url http://localhost:8000]
"""

import argparse
import json
import os
import sys
import time
import httpx

# ---------- Config ----------
DEFAULT_BASE_URL = "http://localhost:8000"
TRANSCRIPT_FILE = os.path.join(
    os.path.dirname(__file__), "data", "transcripts",
    "ANZ_TradeFinance_Discovery_Call_2026-02-04.md",
)

HEADERS = {"Content-Type": "application/json"}  # No API key needed in dev mode


def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def step(num: int, desc: str):
    print(f"\n  [{num}] {desc}")


def ok(msg: str):
    print(f"      -> {msg}")


def fail(msg: str):
    print(f"      !! FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def pretty(data):
    print(json.dumps(data, indent=2, default=str)[:1500])


def run_demo(base: str):
    client = httpx.Client(base_url=base, headers=HEADERS, timeout=60.0)

    # --------------------------------------------------------
    # STEP 1 - Create the deal
    # --------------------------------------------------------
    section("STEP 1: Create Deal - ANZ Bank Trade Finance Platform")

    deal_payload = {
        "accountName": "ANZ Bank",
        "stage": "Discovery",
        "nextCallDate": "2026-02-10",
        "nextCallTime": "10:00",
        "dealAmount": "$4.5M",
        "contactName": "David Chen",
        "contactRole": "Head of Trade Finance Operations",
        "industry": "Banking & Financial Services",
        "description": "Trade Finance Platform modernization - LC automation, AI document processing, compliance",
        "additionalContacts": [
            {"name": "Sarah Mitchell", "role": "VP Technology"},
            {"name": "James Wong", "role": "Director of Digital Transformation"},
        ],
        "notes": "ANZ looking to modernize trade finance. Pain points: 3-4 day processing, paper-based workflows. Interest in AI doc extraction.",
    }

    resp = client.post("/api/deals/create", json=deal_payload)
    if resp.status_code != 200:
        fail(f"Create deal: {resp.status_code} - {resp.text}")
    deal = resp.json()
    deal_id = deal["id"]
    ok(f"Deal created  id={deal_id}  account={deal['accountName']}")

    # --------------------------------------------------------
    # STEP 2 - Pre-call context (inline RAG)
    # --------------------------------------------------------
    section("STEP 2: Pre-Call Agent Populates Context")

    step(1, "Fetching RAG-populated context...")
    resp = client.get(f"/api/deals/{deal_id}/context")
    if resp.status_code != 200:
        fail(f"Deal context: {resp.status_code} - {resp.text}")
    ctx = resp.json()
    ok(f"Similar deals: {len(ctx.get('similarDeals', []))}")
    ok(f"Credible references: {len(ctx.get('credibleReferences', []))}")
    ok(f"Expected question themes: {len(ctx.get('expectedQuestions', []))}")
    ok(f"Talking points: {len(ctx.get('suggestedTalkingPoints', []))}")

    for tp in ctx.get("suggestedTalkingPoints", [])[:3]:
        print(f"        - {tp[:100]}")

    step(2, "Running PreCallPrepAgent (agentic loop)...")
    resp = client.post(f"/api/deals/{deal_id}/agent-prep")
    if resp.status_code == 200:
        agent_result = resp.json()
        ok(f"Agent success={agent_result.get('success')}  confidence={agent_result.get('confidence')}")
        trace = agent_result.get("agent_trace", [])
        for t in trace:
            print(f"        {t['phase']:16s}  {t['description'][:60]:60s}  {t['duration_ms']:.0f}ms")
    else:
        ok(f"Agent endpoint returned {resp.status_code} (may need vector store). Continuing with inline context.")

    # --------------------------------------------------------
    # STEP 3 - Start call + feed mock transcript
    # --------------------------------------------------------
    section("STEP 3: Start Call & Feed Mock Transcript")

    step(1, "Starting call...")
    resp = client.post("/api/calls/start", json={
        "deal_id": deal_id,
        "account_name": "ANZ Bank",
        "contact_name": "David Chen",
    })
    if resp.status_code != 200:
        fail(f"Start call: {resp.status_code} - {resp.text}")
    call_info = resp.json()
    call_id = call_info["call_id"]
    ok(f"Call started  id={call_id}")

    step(2, "Loading ANZ transcript...")
    if not os.path.exists(TRANSCRIPT_FILE):
        fail(f"Transcript file not found: {TRANSCRIPT_FILE}")
    with open(TRANSCRIPT_FILE, "r") as f:
        transcript_text = f.read()
    ok(f"Transcript loaded ({len(transcript_text)} chars)")

    step(3, "Feeding bulk transcript into call...")
    resp = client.post(f"/api/calls/{call_id}/bulk-mock-transcript", json={
        "transcript_text": transcript_text,
        "account_name": "ANZ Bank",
    })
    if resp.status_code != 200:
        fail(f"Bulk transcript: {resp.status_code} - {resp.text}")
    bulk = resp.json()
    ok(f"Chunks added: {bulk.get('chunks_added')}  duration: {bulk.get('total_duration_seconds')}s")

    # --------------------------------------------------------
    # STEP 4 - Push-to-talk query
    # --------------------------------------------------------
    section("STEP 4: Push-to-Talk Query During Call")

    query = "What was CBA's implementation timeline?"
    step(1, f'Query: "{query}"')

    resp = client.post(f"/api/calls/{call_id}/query", json={
        "query": query,
        "deal_id": deal_id,
    })
    if resp.status_code != 200:
        fail(f"Call query: {resp.status_code} - {resp.text}")
    answer = resp.json()
    ok(f"Answer: {answer.get('answer', '')[:200]}")
    ok(f"Source: {answer.get('source_type')}  Confidence: {answer.get('confidence')}")

    # Second demo query
    query2 = "How is SCB handling data privacy?"
    step(2, f'Query: "{query2}"')
    resp = client.post(f"/api/calls/{call_id}/query", json={
        "query": query2,
        "deal_id": deal_id,
    })
    if resp.status_code == 200:
        answer2 = resp.json()
        ok(f"Answer: {answer2.get('answer', '')[:200]}")

    # --------------------------------------------------------
    # STEP 5 - End call + generate summary
    # --------------------------------------------------------
    section("STEP 5: End Call & Generate Post-Call Summary")

    step(1, "Ending call...")
    resp = client.post(f"/api/calls/{call_id}/end")
    if resp.status_code != 200:
        fail(f"End call: {resp.status_code} - {resp.text}")
    end_result = resp.json()
    ok(f"Status: {end_result.get('status')}  Duration: {end_result.get('duration_seconds')}s")

    step(2, "Waiting for summary generation...")
    summary = None
    for attempt in range(15):
        time.sleep(2)
        resp = client.get(f"/api/calls/{call_id}/summary")
        if resp.status_code == 200:
            summary = resp.json()
            break
        print(f"        ... attempt {attempt+1}/15 (summary not ready yet)")

    if not summary:
        fail("Summary was not generated within 30 seconds")

    s = summary.get("summary", {})
    ok(f"Executive Summary: {s.get('executive_summary', '')[:150]}...")
    ok(f"Deal Health Score: {s.get('deal_health_score')}/10")
    ok(f"Deal Health Reason: {s.get('deal_health_reason', '')[:120]}")
    ok(f"Key Points: {len(s.get('key_points', []))}")
    ok(f"Pain Points: {len(s.get('pain_points', []))}")
    ok(f"Action Items: {len(summary.get('action_items', []))}")

    for item in summary.get("action_items", [])[:5]:
        print(f"        - [{item.get('priority', '?').upper()}] {item.get('task', '')[:80]}  (owner: {item.get('owner', '?')})")

    # --------------------------------------------------------
    # STEP 6 - Approve MoM + write to SharePoint
    # --------------------------------------------------------
    section("STEP 6: Seller Approves -> MoM Written to SharePoint")

    step(1, "Approving summary and writing MoM to SharePoint...")
    resp = client.post(f"/api/calls/{call_id}/approve-mom", json={
        "approved": True,
        "sharepoint_folder": "/sites/DealSense/Shared Documents/MoMs",
        "additional_notes": "Follow up with ANZ technical team re: architecture deep-dive next week.",
    })
    if resp.status_code != 200:
        fail(f"Approve MoM: {resp.status_code} - {resp.text}")
    mom_result = resp.json()
    sp = mom_result.get("sharepoint", {})
    ok(f"Status: {mom_result.get('status')}")
    ok(f"Method: {sp.get('method')}")
    ok(f"File: {sp.get('file_name')}")
    ok(f"URL: {sp.get('web_url')}")

    step(2, "MoM preview (first 500 chars):")
    print(mom_result.get("mom_preview", "")[:500])

    # --------------------------------------------------------
    # Done!
    # --------------------------------------------------------
    section("DEMO COMPLETE")
    print(f"""
  All 6 steps completed successfully.

  Summary:
    Deal ID:     {deal_id}
    Call ID:     {call_id}
    Health:      {s.get('deal_health_score')}/10
    Actions:     {len(summary.get('action_items', []))} items
    SharePoint:  {sp.get('web_url', 'N/A')}

  Endpoints exercised:
    POST /api/deals/create
    GET  /api/deals/{deal_id}/context
    POST /api/deals/{deal_id}/agent-prep
    POST /api/calls/start
    POST /api/calls/{call_id}/bulk-mock-transcript
    POST /api/calls/{call_id}/query
    POST /api/calls/{call_id}/end
    GET  /api/calls/{call_id}/summary
    POST /api/calls/{call_id}/approve-mom
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DealSense AI End-to-End Demo")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Backend URL")
    args = parser.parse_args()

    print("DealSense AI - End-to-End Demo")
    print(f"Backend: {args.base_url}")
    run_demo(args.base_url)
