from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel

app = FastAPI()

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Deal(BaseModel):
    id: int
    title: str
    summary: str
    solutionArea: str
    industry: str
    benchmark: str
    caseStudy: str
    teamSize: str
    keyHighlights: List[str]
    dealBreakers: List[str]
    dealValue: str
    duration: str

# Mock data (from mockData.js)
MOCK_DEALS = [
    Deal(
        id=1,
        title="Global Banking Platform Migration",
        summary="Successfully migrated core banking operations to cloud-native architecture with zero downtime",
        solutionArea="Cloud Infrastructure & Digital Transformation",
        industry="Banking & Financial Services",
        benchmark="Banking Solution",
        caseStudy="Enterprise deployed a comprehensive banking platform supporting 500+ branches across 25 countries. Implementation included real-time transaction processing, compliance frameworks (PCI-DSS, GDPR), and 99.99% uptime SLA.",
        teamSize="12 members (architects, engineers, compliance specialists)",
        keyHighlights=[
            "24/7 transaction processing with <100ms latency",
            "Full compliance with international banking regulations",
            "50% reduction in infrastructure costs",
            "Seamless integration with existing systems",
        ],
        dealBreakers=[
            "Requires strict data residency compliance",
            "Long sales cycle (9-12 months)",
            "High initial infrastructure investment",
        ],
        dealValue="$2.4M",
        duration="18 months",
    ),
    Deal(
        id=2,
        title="Insurance Claims Processing Automation",
        summary="Automated claims processing with AI-driven validation and reduced processing time by 70%",
        solutionArea="Business Process Automation",
        industry="Insurance & Risk Management",
        benchmark="Banking Solution",
        caseStudy="Insurance provider implemented intelligent claims processing system handling 500K+ claims annually. System includes automated validation, fraud detection, and escalation workflows.",
        teamSize="8 members (automation engineers, QA, business analysts)",
        keyHighlights=[
            "70% reduction in processing time (45 days → 14 days)",
            "99.2% accuracy in claims validation",
            "Significant reduction in fraud detection time",
            "Improved customer satisfaction scores by 35%",
        ],
        dealBreakers=[
            "Requires historical claims data for ML training",
            "Change management needed across 200+ staff",
            "Complex legacy system integrations",
        ],
        dealValue="$1.8M",
        duration="14 months",
    ),
    Deal(
        id=3,
        title="Customer Data Platform Implementation",
        summary="Unified customer data platform integrating 15+ data sources with real-time analytics",
        solutionArea="Data & Analytics",
        industry="Retail & E-commerce",
        benchmark="Banking Solution",
        caseStudy="Retail organization consolidated customer data from online, mobile, and physical channels. Platform provides 360-degree customer view with real-time personalization capabilities.",
        teamSize="10 members (data engineers, analysts, architects)",
        keyHighlights=[
            "Single customer view across all channels",
            "Real-time personalization capability",
            "Enabled targeted marketing with 40% higher ROI",
            "Data governance and compliance built-in",
        ],
        dealBreakers=[
            "Requires 6+ months of data migration",
            "Complex ETL pipeline development",
            "Ongoing data quality management needed",
        ],
        dealValue="$2.1M",
        duration="16 months",
    ),
    Deal(
        id=4,
        title="Supply Chain Visibility Network",
        summary="End-to-end supply chain transparency with real-time tracking and predictive analytics",
        solutionArea="Supply Chain & Operations",
        industry="Manufacturing & Logistics",
        benchmark="Banking Solution",
        caseStudy="Global manufacturer implemented supply chain network tracking 10K+ suppliers and 1M+ shipments daily. System provides real-time visibility and predictive demand forecasting.",
        teamSize="9 members (supply chain experts, engineers, data scientists)",
        keyHighlights=[
            "Real-time visibility of 1M+ daily shipments",
            "Predictive demand forecasting accuracy: 92%",
            "15% reduction in inventory carrying costs",
            "Improved supplier collaboration metrics",
        ],
        dealBreakers=[
            "Requires supplier API integrations",
            "Data standardization across global operations",
            "Complex stakeholder alignment",
        ],
        dealValue="$2.8M",
        duration="20 months",
    ),
    Deal(
        id=5,
        title="Healthcare Patient Management System",
        summary="Integrated patient management platform serving 15 hospital networks with 200K+ patients",
        solutionArea="Healthcare IT & Patient Care",
        industry="Healthcare & Life Sciences",
        benchmark="Banking Solution",
        caseStudy="Healthcare network unified patient records across 15 hospitals and 50+ clinics. System includes EHR integration, appointment scheduling, telemedicine capabilities, and HL7 compliance.",
        teamSize="11 members (healthcare IT specialists, compliance, developers)",
        keyHighlights=[
            "Integrated 200K+ patient records",
            "30% reduction in appointment wait times",
            "Full HL7 and HIPAA compliance",
            "Telemedicine capabilities with 500K+ annual consultations",
        ],
        dealBreakers=[
            "Strict HIPAA and data privacy requirements",
            "Complex EHR system integrations",
            "Regulatory approval cycles (3-6 months)",
        ],
        dealValue="$3.2M",
        duration="22 months",
    ),
]

@app.get("/api/deals", response_model=List[Deal])
def get_deals():
    return MOCK_DEALS


@app.get("/api/search", response_model=List[Deal])
def search_deals(q: str = "", limit: int = 10):
    """
    Simple search endpoint over mock deals.
    - q: query string (matches title, summary, caseStudy, solutionArea, industry)
    - limit: maximum number of results to return
    Returns full list when q is empty.
    """
    if not q:
        return MOCK_DEALS[:limit]

    ql = q.lower()

    def matches(d: Deal) -> bool:
        hay = f"{d.title} {d.summary} {d.caseStudy} {d.solutionArea} {d.industry}".lower()
        return ql in hay

    results = [d for d in MOCK_DEALS if matches(d)]
    return results[:limit]
