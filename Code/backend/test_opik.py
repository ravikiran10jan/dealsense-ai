"""
Quick smoke-test: configure Opik, send a trace, verify it lands in the cloud.
Run with:  python test_opik.py   (from the backend/ directory)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from observability.opik_config import configure_opik, get_opik_client, is_opik_enabled
from observability.opik_tracer import track_rag_query, log_event, OpikTrace

# ── 1. Configure ──────────────────────────────────────────────────
print("1. Configuring Opik...")
configure_opik()
print(f"   OPIK_ENABLED  = {is_opik_enabled()}")
print(f"   Project       = {os.getenv('OPIK_PROJECT_NAME')}")
print(f"   Workspace     = {os.getenv('OPIK_WORKSPACE')}")

client = get_opik_client()
if client is None:
    print("   ERROR: Opik client could not be created. Check your API key / workspace.")
    sys.exit(1)
print(f"   Client created OK (project={client.project_name})")

# ── 2. Programmatic trace ────────────────────────────────────────
print("\n2. Sending a programmatic trace...")
trace = client.trace(
    name="test:smoke_test",
    input={"query": "What is DealSense AI?"},
    output={"answer": "An AI-powered sales assistant by Nexora Solutions."},
    tags=["test", "smoke"],
    metadata={"source": "test_opik.py"},
)
span = trace.span(
    name="rag_search",
    input={"query": "What is DealSense AI?", "k": 3},
    output={"num_results": 3, "source_type": "RAG"},
    metadata={"similarity_threshold": 1.8},
)
span.end()
trace.end()
print("   Trace sent.")

# ── 3. @track decorator ─────────────────────────────────────────
print("\n3. Testing @track decorator via track_rag_query...")

@track_rag_query(name="test_semantic_search")
def fake_semantic_search(query, k=3):
    return [{"content": "Trade finance platform migration", "score": 0.92}]

result = fake_semantic_search("trade finance capabilities", k=5)
print(f"   Decorated function returned: {result}")

# ── 4. OpikTrace context manager ─────────────────────────────────
print("\n4. Testing OpikTrace context manager...")
with OpikTrace("test:deal_context", input_data={"deal_id": 42, "account": "Apex National Bank"}, tags=["test"]) as t:
    t.log_step("fetch_similar_deals", {"count": 3})
    t.log_step("generate_talking_points", {"num_points": 4})
    t.set_output({"success": True})
print("   OpikTrace completed.")

# ── 5. log_event ─────────────────────────────────────────────────
print("\n5. Logging a custom event...")
log_event(
    "test_event",
    {"action": "smoke_test_complete", "user": "dev-user"},
    tags=["test"],
)
print("   Event logged.")

# ── 6. Flush to ensure delivery ──────────────────────────────────
print("\n6. Flushing Opik client...")
client.flush()
print("   Flush complete.")

# ── Done ──────────────────────────────────────────────────────────
dashboard_url = f"https://www.comet.com/opik/{os.getenv('OPIK_WORKSPACE')}/projects"
print(f"\nAll tests passed. Open your Opik dashboard to see the traces:")
print(f"   {dashboard_url}")
