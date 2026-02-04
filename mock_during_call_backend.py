from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CallIteration(BaseModel):
    id: int
    title: str
    description: str
    industry: str
    teamSize: str
    budget: str
    timeline: str
    status: str
    caseStudy: str
    keyHighlights: List[str]
    dealBreakers: List[str]
    successCriteria: List[str]

# Example: 3 call iterations for the same deal
MOCK_DURING_CALLS = [
    CallIteration(
        id=1,
        title="Global Banking Platform Migration",
        description="Comprehensive cloud migration for a major banking institution with global operations",
        industry="Banking & Financial Services",
        teamSize="12 members",
        budget="$2.4M",
        timeline="18 months",
        status="Active",
        caseStudy="Enterprise deployed a comprehensive banking platform supporting 500+ branches across 25 countries. Implementation included real-time transaction processing, compliance frameworks (PCI-DSS, GDPR), and 99.99% uptime SLA. The migration was completed with zero customer downtime through careful orchestration and failover strategies.",
        keyHighlights=[
            "24/7 transaction processing with <100ms latency across all regions",
            "Full compliance with international banking regulations (PCI-DSS, GDPR, SOX)",
            "50% reduction in infrastructure costs through cloud optimization",
            "Seamless integration with existing customer-facing systems",
            "Enhanced security with end-to-end encryption and zero-trust architecture",
        ],
        dealBreakers=[
            "Requires strict data residency compliance in specific geographic regions",
            "Long sales cycle (9-12 months) due to regulatory approval requirements",
            "High initial infrastructure investment ($500K+ upfront)",
            "Ongoing licensing and support costs (15% of project cost annually)",
        ],
        successCriteria=[
            "Zero customer impact during migration",
            "All regulatory audits passed",
            "Cost savings within 18 months",
            "System availability > 99.99%",
        ],
    ),
    CallIteration(
        id=2,
        title="Global Banking Platform Migration",
        description="Second call: Focused on compliance and risk management for the migration.",
        industry="Banking & Financial Services",
        teamSize="12 members",
        budget="$2.4M",
        timeline="18 months",
        status="In Progress",
        caseStudy="Discussed compliance frameworks and risk mitigation strategies. Addressed regulatory requirements and data residency concerns.",
        keyHighlights=[
            "Compliance frameworks reviewed",
            "Risk management plan established",
            "Stakeholder alignment achieved",
        ],
        dealBreakers=[
            "Pending regulatory approval",
            "Unresolved data residency issues",
        ],
        successCriteria=[
            "Regulatory approval obtained",
            "Risk register updated",
        ],
    ),
    CallIteration(
        id=3,
        title="Global Banking Platform Migration",
        description="Third call: Technical deep dive and migration timeline planning.",
        industry="Banking & Financial Services",
        teamSize="12 members",
        budget="$2.4M",
        timeline="18 months",
        status="Completed",
        caseStudy="Technical team presented migration plan, discussed phased rollout, and finalized timeline.",
        keyHighlights=[
            "Phased migration plan approved",
            "Timeline finalized",
            "Technical risks addressed",
        ],
        dealBreakers=[
            "Resource constraints for rollout",
        ],
        successCriteria=[
            "Migration plan signed off",
            "All technical risks mitigated",
        ],
    ),
]

@app.get("/api/during_call", response_model=List[CallIteration])
def get_during_call_iterations():
    return MOCK_DURING_CALLS
