// Python backend style mock data for deals
export const mockDealsPython = [
  {
    title: "Global Banking Platform Migration",
    summary: "Successfully migrated core banking operations to cloud-native architecture with zero downtime",
    team_size: 12,
    solution_area: "Cloud Infrastructure & Digital Transformation",
    industry_benchmark: "Banking Solution",
    key_highlights: [
      "24/7 transaction processing with <100ms latency",
      "Full compliance with international banking regulations",
      "50% reduction in infrastructure costs",
      "Seamless integration with existing systems"
    ],
    deal_breakers: [
      "Requires strict data residency compliance",
      "Long sales cycle (9-12 months)",
      "High initial infrastructure investment"
    ]
  },
  {
    title: "Insurance Claims Processing Automation",
    summary: "Automated claims processing with AI-driven validation and reduced processing time by 70%",
    team_size: 8,
    solution_area: "Business Process Automation",
    industry_benchmark: "Banking Solution",
    key_highlights: [
      "70% reduction in processing time (45 days → 14 days)",
      "99.2% accuracy in claims validation",
      "Significant reduction in fraud detection time",
      "Improved customer satisfaction scores by 35%"
    ],
    deal_breakers: [
      "Requires historical claims data for ML training",
      "Change management needed across 200+ staff",
      "Complex legacy system integrations"
    ]
  },
  {
    title: "Customer Data Platform Implementation",
    summary: "Unified customer data platform integrating 15+ data sources with real-time analytics",
    team_size: 10,
    solution_area: "Data & Analytics",
    industry_benchmark: "Banking Solution",
    key_highlights: [
      "Single customer view across all channels",
      "Real-time personalization capability",
      "Enabled targeted marketing with 40% higher ROI",
      "Data governance and compliance built-in"
    ],
    deal_breakers: [
      "Requires 6+ months of data migration",
      "Complex ETL pipeline development",
      "Ongoing data quality management needed"
    ]
  },
  {
    title: "Supply Chain Visibility Network",
    summary: "End-to-end supply chain transparency with real-time tracking and predictive analytics",
    team_size: 9,
    solution_area: "Supply Chain & Operations",
    industry_benchmark: "Banking Solution",
    key_highlights: [
      "Real-time visibility of 1M+ daily shipments",
      "Predictive demand forecasting accuracy: 92%",
      "15% reduction in inventory carrying costs",
      "Improved supplier collaboration metrics"
    ],
    deal_breakers: [
      "Requires supplier API integrations",
      "Data standardization across global operations",
      "Complex stakeholder alignment"
    ]
  },
  {
    title: "Healthcare Patient Management System",
    summary: "Integrated patient management platform serving 15 hospital networks with 200K+ patients",
    team_size: 11,
    solution_area: "Healthcare IT & Patient Care",
    industry_benchmark: "Banking Solution",
    key_highlights: [
      "Integrated 200K+ patient records",
      "30% reduction in appointment wait times",
      "Full HL7 and HIPAA compliance",
      "Telemedicine capabilities with 500K+ annual consultations"
    ],
    deal_breakers: [
      "Strict HIPAA and data privacy requirements",
      "Complex EHR system integrations",
      "Regulatory approval cycles (3-6 months)"
    ]
  }
];
/**
 * Mock data for Top 5 Deals
 * Simulates historical business deals with key metrics and insights
 */

export const mockDeals = [
  {
    id: 1,
    title: "Global Banking Platform Migration",
    summary: "Successfully migrated core banking operations to cloud-native architecture with zero downtime",
    solutionArea: "Cloud Infrastructure & Digital Transformation",
    industry: "Banking & Financial Services",
    benchmark: "Banking Solution",
    caseStudy:
      "Enterprise deployed a comprehensive banking platform supporting 500+ branches across 25 countries. Implementation included real-time transaction processing, compliance frameworks (PCI-DSS, GDPR), and 99.99% uptime SLA.",
    teamSize: "12 members (architects, engineers, compliance specialists)",
    keyHighlights: [
      "24/7 transaction processing with <100ms latency",
      "Full compliance with international banking regulations",
      "50% reduction in infrastructure costs",
      "Seamless integration with existing systems",
    ],
    dealBreakers: [
      "Requires strict data residency compliance",
      "Long sales cycle (9-12 months)",
      "High initial infrastructure investment",
    ],
    dealValue: "$2.4M",
    duration: "18 months",
  },
  {
    id: 2,
    title: "Insurance Claims Processing Automation",
    summary: "Automated claims processing with AI-driven validation and reduced processing time by 70%",
    solutionArea: "Business Process Automation",
    industry: "Insurance & Risk Management",
    benchmark: "Banking Solution",
    caseStudy:
      "Insurance provider implemented intelligent claims processing system handling 500K+ claims annually. System includes automated validation, fraud detection, and escalation workflows.",
    teamSize: "8 members (automation engineers, QA, business analysts)",
    keyHighlights: [
      "70% reduction in processing time (45 days → 14 days)",
      "99.2% accuracy in claims validation",
      "Significant reduction in fraud detection time",
      "Improved customer satisfaction scores by 35%",
    ],
    dealBreakers: [
      "Requires historical claims data for ML training",
      "Change management needed across 200+ staff",
      "Complex legacy system integrations",
    ],
    dealValue: "$1.8M",
    duration: "14 months",
  },
  {
    id: 3,
    title: "Customer Data Platform Implementation",
    summary: "Unified customer data platform integrating 15+ data sources with real-time analytics",
    solutionArea: "Data & Analytics",
    industry: "Retail & E-commerce",
    benchmark: "Banking Solution",
    caseStudy:
      "Retail organization consolidated customer data from online, mobile, and physical channels. Platform provides 360-degree customer view with real-time personalization capabilities.",
    teamSize: "10 members (data engineers, analysts, architects)",
    keyHighlights: [
      "Single customer view across all channels",
      "Real-time personalization capability",
      "Enabled targeted marketing with 40% higher ROI",
      "Data governance and compliance built-in",
    ],
    dealBreakers: [
      "Requires 6+ months of data migration",
      "Complex ETL pipeline development",
      "Ongoing data quality management needed",
    ],
    dealValue: "$2.1M",
    duration: "16 months",
  },
  {
    id: 4,
    title: "Supply Chain Visibility Network",
    summary: "End-to-end supply chain transparency with real-time tracking and predictive analytics",
    solutionArea: "Supply Chain & Operations",
    industry: "Manufacturing & Logistics",
    benchmark: "Banking Solution",
    caseStudy:
      "Global manufacturer implemented supply chain network tracking 10K+ suppliers and 1M+ shipments daily. System provides real-time visibility and predictive demand forecasting.",
    teamSize: "9 members (supply chain experts, engineers, data scientists)",
    keyHighlights: [
      "Real-time visibility of 1M+ daily shipments",
      "Predictive demand forecasting accuracy: 92%",
      "15% reduction in inventory carrying costs",
      "Improved supplier collaboration metrics",
    ],
    dealBreakers: [
      "Requires supplier API integrations",
      "Data standardization across global operations",
      "Complex stakeholder alignment",
    ],
    dealValue: "$2.8M",
    duration: "20 months",
  },
  {
    id: 5,
    title: "Healthcare Patient Management System",
    summary: "Integrated patient management platform serving 15 hospital networks with 200K+ patients",
    solutionArea: "Healthcare IT & Patient Care",
    industry: "Healthcare & Life Sciences",
    benchmark: "Banking Solution",
    caseStudy:
      "Healthcare network unified patient records across 15 hospitals and 50+ clinics. System includes EHR integration, appointment scheduling, telemedicine capabilities, and HL7 compliance.",
    teamSize: "11 members (healthcare IT specialists, compliance, developers)",
    keyHighlights: [
      "Integrated 200K+ patient records",
      "30% reduction in appointment wait times",
      "Full HL7 and HIPAA compliance",
      "Telemedicine capabilities with 500K+ annual consultations",
    ],
    dealBreakers: [
      "Strict HIPAA and data privacy requirements",
      "Complex EHR system integrations",
      "Regulatory approval cycles (3-6 months)",
    ],
    dealValue: "$3.2M",
    duration: "22 months",
  },
];

/**
 * Mock data for a single deal's detailed information
 * Used in "During Call" tab
 */
export const mockDealDetails = {
  id: 1,
  title: "Global Banking Platform Migration",
  description:
    "Comprehensive cloud migration for a major banking institution with global operations",
  industry: "Banking & Financial Services",
  teamSize: "12 members",
  budget: "$2.4M",
  timeline: "18 months",
  status: "Active",
  caseStudy:
    "Enterprise deployed a comprehensive banking platform supporting 500+ branches across 25 countries. Implementation included real-time transaction processing, compliance frameworks (PCI-DSS, GDPR), and 99.99% uptime SLA. The migration was completed with zero customer downtime through careful orchestration and failover strategies.",
  keyHighlights: [
    "24/7 transaction processing with <100ms latency across all regions",
    "Full compliance with international banking regulations (PCI-DSS, GDPR, SOX)",
    "50% reduction in infrastructure costs through cloud optimization",
    "Seamless integration with existing customer-facing systems",
    "Enhanced security with end-to-end encryption and zero-trust architecture",
  ],
  dealBreakers: [
    "Requires strict data residency compliance in specific geographic regions",
    "Long sales cycle (9-12 months) due to regulatory approval requirements",
    "High initial infrastructure investment ($500K+ upfront)",
    "Ongoing licensing and support costs (15% of project cost annually)",
  ],
  successCriteria: [
    "Zero customer impact during migration",
    "All regulatory audits passed",
    "Cost savings within 18 months",
    "System availability > 99.99%",
  ],
};

/**
 * Mock sample pre-call notes
 * Used as template in "Before Call" tab
 */
export const mockPreCallNotes = `
Key Talking Points:
- Focus on compliance requirements and regulatory alignment
- Emphasize cost optimization and ROI timeline
- Highlight reference customer success story
- Address data residency concerns upfront

Risks to Monitor:
- Long implementation timeline may impact budget approval
- Legacy system integration complexity
- Change management requirements across organization

Discussion Topics:
- Current infrastructure pain points
- Timeline flexibility and phased approach options
- Support and maintenance model preferences
`;

/**
 * Mock post-call summary template
 * Used in "After Call" tab
 */
export const mockPostCallSummary = {
  dealTitle: "Global Banking Platform Migration",
  callDate: new Date().toISOString().split("T")[0],
  finalHighlights: "",
  risks: "",
  callOutcome: "Follow-up",
  nextSteps: "",
  clientFeedback: "",
  decidedFeatures: [],
};
