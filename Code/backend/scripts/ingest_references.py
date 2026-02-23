#!/usr/bin/env python3
"""
Script to ingest reference contacts and person profiles into the vector store.
Updated with full LinkedIn profile data.
Run from backend directory: python scripts/ingest_references.py
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.deal_ingestion import ingest_person_to_vector_store, ingest_reference_contact


def ingest_arjun_mehta():
    """Ingest Arjun Mehta's full profile"""
    return ingest_person_to_vector_store(
        person_name="Arjun Mehta",
        title="Head of A/NZ Banking and Capital Markets Solutions Sales",
        company="Nexora Technologies (Nexora Solutions)",
        linkedin_url="https://www.linkedin.com/in/example-profile/",
        content="""Arjun Mehta is the Head of A/NZ Banking and Capital Markets Solutions Sales at Nexora Technologies, based in Greater Sydney Area.

ABOUT:
Nexora Solutions is an international consultancy specialising in Banking & Capital Markets technology with a focus on consulting, advisory, analytics, engineering and vendor platform integration.

With over 10,000 delivery consultants globally, delivering in a hybrid on/nearshore capacity, our services span Global Markets, Commodities, Asset & Wealth Management, Private Banking & Commercial/Institutional Banking.

We work with financial services organisations in the following domains:
- Global Markets / Investment Banking
- Asset Management / Hedge Funds / PE
- Wealth Management / Private Banking
- Commercial Banking
- Commodities (Physical & Derivatives)

Contact: arjun.mehta@nexora.com

CURRENT ROLE:
Nexora Banking and Capital Markets A/NZ Practice Lead at Nexora Technologies (Apr 2020 - Present, 5+ years)
Sydney, New South Wales, Australia

Using 20+ years' experience in hands-on delivery to help drive growth of Banking and Capital Markets consulting, analytics, vendor and engineering services businesses in the A/NZ region.

Skills: Operating Models, Sales Target Management, Business Development

EXPERIENCE AT NEXORA FINANCIAL SERVICES (15+ years):

Director - Head of Vendor Solutions (Australia)
May 2018 - Present (7+ years)
Melbourne and Sydney Area, Australia

Head of Australia
May 2015 - Apr 2020 (5 years)
Greater Sydney Area
Director leading APAC business: Packaged Services (TradeSys, Calypso, Openlink) and Technical Consulting teams

Head of Technical Consulting & Delivery for Australia and Asia-Pacific
May 2010 - Oct 2017 (7+ years)
Melbourne and Sydney Area, Australia
- Principal Technical Consultant with responsibilities including sales, pre-sales, onsite consultancy and new business strategy
- Leading HPC, development and financial engineering team spread across Sydney and Melbourne
- Managing and expanding Nexora Australia and Asia Pacific technical consultancy business
- Specialising in High Performance Technologies: Data caching (Gemfire, Coherence), Grid Computing (Platform Symphony, Tibco DataSynapse, Microsoft HPC Server), High Frequency Trading Platforms (CEP, Apama)
- Development Services and Risk Systems (CCR, CVA, Market Risk, Operational Risk)
- Certified in MS HPC Server, IBM Platform and Tibco DataSynapse technologies
- On-site consultant leading teams delivering CCR/CVA solutions at banks in APAC region
- Building cloud solutions for financial companies using third-party data centre infrastructure
- Hosting CCR Community of Practice with leading Risk IT leaders

PREVIOUS EXPERIENCE:

Sterling Capital (3 years 2 months):
- Assistant Vice President: WebLogic Applications Grid Technical Lead (Dec 2008 - Oct 2009)
  - WebLogic Application Grid Architect: Oracle 11g WAG integration
  - Focus on Coherence and Oracle Enterprise Manager technologies
  - Project managing WebLogic and Data grid farm service using Oracle Coherence and DataSynapse
  - Architect for local and global data-grid solutions using Coherence
  - Put forward for Oracle 11g Application Grid Excellence Award
  - Architecting cloud HPC/data grid initiative

- HPC Grid Architect (Sep 2006 - Dec 2008)
  - Designing and implementing HPC and grid solutions across Sterling Capital
  - DataSynapse engineer migrating grids across regions: London, New York, Singapore, Tokyo
  - HPC scavenging project saved bank over £X million
  - Part of IB team for Cloud computing solutions
  - Presented at Managing The Grid conference London 2008

Alpine Investment Bank - Associate Director (Nov 2000 - Sep 2006, 5+ years)
- Team Leader of Global Service Delivery IRD Structured Products
- Implementing and supporting trade capture, risk management and pricing systems
- Managing team of 8 globally across New York, London, Singapore, Hong Kong

Swiss National Capital - Intern (1999)

EXPERTISE AREAS:
- Banking & Capital Markets Technology
- Vendor Solutions (TradeSys, Calypso, Openlink)
- High Performance Computing (HPC) and Grid Computing
- Risk Systems (CCR, CVA, Market Risk, Operational Risk)
- Data Caching (Gemfire, Coherence)
- High Frequency Trading Platforms
- Cloud Solutions for Financial Services
- Team Leadership and Delivery Management
- APAC Regional Business Development""",
        metadata={
            "region": "Asia-Pacific",
            "expertise": "Banking & Capital Markets, Vendor Solutions, HPC, Risk Systems",
            "email": "arjun.mehta@nexora.com",
        }
    )


def ingest_thomas_blake():
    """Ingest Thomas Blake's full profile"""
    return ingest_person_to_vector_store(
        person_name="Thomas Blake",
        title="CIO, Trade and Working Capital",
        company="Eastern Commerce Bank",
        linkedin_url="https://www.linkedin.com/in/example-profile/",
        content="""Thomas Blake is the CIO, Trade and Working Capital at Eastern Commerce Bank, based in Singapore.

CURRENT ROLE:
CIO, Trade and Working Capital at Eastern Commerce Bank
Feb 2024 - Present (2+ years)
Singapore
Full-time

EXPERIENCE AT EASTERN COMMERCE BANK (10+ years):

MD - Global Head, FM Trade Processing and Post Trade Technology
Feb 2017 - Feb 2024 (7 years)
Singapore

MD - Global Head of Financial Markets Operations Technology
May 2015 - Feb 2017 (1 year 10 months)
Singapore

PREVIOUS EXPERIENCE:

Head of IT at ClearTrade (Pacific Securities Group)
Jun 2010 - Apr 2015 (4 years 11 months)
Singapore

Head of Operations, South East Asia, Global Broker Services at Global Brokerage (Formally Coexis)
Aug 2008 - Jun 2010 (1 year 11 months)
Singapore

Legacy Financial (8+ years):
- Head of Operations Technology Asia
- Head of IT South East Asia
- SVP
Jun 2000 - Aug 2008
Singapore

Associate Director at Northern Markets
1998 - 2000 (2 years)
London Area, United Kingdom

EDUCATION:
University of Bradford (1989 - 1993)

CERTIFICATIONS:
- Microsoft Certified: Azure Fundamentals (Issued May 2021)
- Data Analysis with Python - Coursera (Issued Mar 2021)

EXPERTISE AREAS:
- Trade and Working Capital Technology
- Financial Markets Operations Technology
- Post Trade Technology
- Operations Technology Leadership
- Banking Technology in Asia Pacific
- Digital Transformation in Financial Services
- Cloud Technologies (Azure certified)
- Data Analysis

KEY ACHIEVEMENTS:
- Over 25 years of experience in financial services technology
- Led global teams across Trade Processing and Post Trade Technology
- Experience across major financial institutions: Eastern Commerce Bank, Legacy Financial, Northern Markets
- Deep expertise in Singapore and Asia-Pacific financial markets
- Pioneer in trade finance technology and operations""",
        metadata={
            "region": "Asia-Pacific",
            "location": "Singapore",
            "expertise": "Trade Finance, Post Trade Technology, Operations Technology",
            "reference_type": "credible_reference",
            "relationship": "Reference client - Trade and Working Capital Technology",
        }
    )


def ingest_omar_hassan():
    """Ingest Omar Hassan's full profile"""
    return ingest_person_to_vector_store(
        person_name="Omar Hassan",
        title="EVP - Global Head FSI Solutions",
        company="Nexora Technologies",
        linkedin_url="https://www.linkedin.com/in/example-profile/",
        content="""Omar Hassan is the EVP and Global Head of FSI Solutions at Nexora Technologies, based in London Area, United Kingdom.

ABOUT:
EVP @ Nexora | Financial Services, RegTech, Cloud & AI. I have solid experience building Trading and Risk Management practices. Over time, my responsibilities have expanded to cover Banking and Insurance. In my current role as Head of FSI Solutions at Nexora, I focus on driving growth through a consultative sales approach. My main focus areas are modernization, compliance, and innovation through AI. We help clients improve profitability by supporting both revenue-generating initiatives and cost optimization. I have achieved continuous growth over the years and take pride in delivering results. While I have a global remit, I stay quite close to our clients in the different regions.

CURRENT ROLE AT NEXORA TECHNOLOGIES (1 year 9 months):

Financial Services Industry - Global Head FSI Solutions
May 2025 - Present (10 months)
London Area, United Kingdom · Hybrid, Full-time
I lead FSI Capital Markets, Banking and Insurance solutions within Consulting & Engineering Services at Nexora

Financial Services Industry - Global Head Capital Markets Solutions
Jun 2024 - Apr 2025 (11 months)

EXPERIENCE AT NEXORA (7 years 8 months):

Global Head Trading and Risk Management Solutions
Feb 2021 - May 2024 (3 years 4 months)
Greater London, England, United Kingdom · Hybrid, Full-time
- Global head of practice
- Global P&L ownership - 1100+ headcount; 140M+ yearly target revenue
- Consistently overperforming for the last 5 years with 15% to 20% growth YoY
- Treasury, Sell-side, Buy-side, Commodity, Corporate lending, Reg Reporting, Data Management, Trade Surveillance, Liquidity management, Cloud
- TradeSys, Calypso, Finastra, Orchestrade, AxiomSL, Moody's
Skills: Business Case Preparation, Customer Service Management

EMEA Head of Vendor Solutions
Oct 2016 - Jan 2021 (4 years 4 months)
London Area, United Kingdom
- P&L ownership in EMEA; 500+ headcount; 45M yearly target revenue
- Consistently overperforming YoY
- TradeSys, Calypso, Finastra, Orchestrade, AxiomSL, Moody's
Skills: Business Case Preparation, Programme Delivery

PREVIOUS EXPERIENCE:

Director - Head of Financial Services practice at ConsultCo
Feb 2011 - Sep 2016 (5 years 8 months)
Dubai / Paris
ConsultCo is a global Consulting company specialised in software development and deployment in Europe, Middle East and Africa. ConsultCo operate out of 5 offices in Paris, Dubai, Tunis, Algiers and Abidjan.
- Launched and developed the Financial Services practice
- Launched and managed 2 new offices in Paris (2011 - 2014) and Dubai (2014 - 2016)
- 100+ headcount, started the practice from 0 and reached 5M revenue per year
Skills: Business Case Preparation, Programme Delivery

Principal at TradeSys
Jan 2005 - Feb 2011 (6 years 2 months)
Greater Paris Metropolitan Region
TradeSys is the leading provider of cross-asset trading, risk management and processing solutions.
- Co-launched the professional services department
- Built project methodologies (MXpress, FEM, MXplus)
- Managed the deployment of project methodologies in regions (EMEA / NA / APAC)
- Built sales proposals and responses to RFPs
- Was actively involved in internal consulting, marketing campaigns, training initiatives and alliance management
- Was actively involved in several projects delivery and support as a TradeSys expert and project manager
Skills: Programme Delivery, Communication

Consultant - Prime Brokerage at Continental Bank
Sep 2003 - Dec 2004 (1 year 4 months)
Greater Paris Metropolitan Region
- Prime Brokerage business
- Client services (MO / BO)
- TradeSys expertise
- Reporting / Accounting / P&L calculation
- Settlements - Swifts
Skills: Communication

EXPERTISE AREAS:
- Financial Services Industry (FSI) Solutions
- Capital Markets Solutions
- Banking and Insurance Solutions
- Trading and Risk Management
- RegTech and Compliance
- Cloud and AI Innovation
- Vendor Solutions (TradeSys, Calypso, Finastra, Orchestrade, AxiomSL, Moody's)
- Treasury and Liquidity Management
- Trade Surveillance and Data Management
- Global P&L Management
- Consultative Sales and Business Development
- Team Leadership (1100+ headcount globally)

KEY ACHIEVEMENTS:
- Manages 140M+ yearly target revenue with consistent 15-20% YoY growth
- Built and scaled multiple practices from zero to significant revenue
- Global reach across EMEA, NA, and APAC regions
- Expert in modernization, compliance, and AI-driven innovation for financial services""",
        metadata={
            "region": "Global",
            "location": "London",
            "expertise": "FSI Solutions, Capital Markets, Trading & Risk Management, RegTech, Cloud & AI",
            "reference_type": "nexora_leadership",
            "relationship": "Nexora Global FSI Solutions Leader",
        }
    )


def ingest_vikram_patel():
    """Ingest Vikram Patel's full profile"""
    return ingest_person_to_vector_store(
        person_name="Vikram Patel",
        title="Director",
        company="Nexora",
        linkedin_url="https://www.linkedin.com/in/example-profile/",
        content="""Vikram Patel is a Director at Nexora, based in Singapore.

ABOUT:
I am an Account Manager / Project Manager / Business Analyst with 16+ years of experience leading cross-functional teams in the development and delivery of programs across various leading Global investment banks in APAC.

CURRENT ROLE:
Director at Nexora
Oct 2017 - Present (8 years 5 months)
Singapore · On-site, Full-time

At Nexora, I lead delivery and client engagement for APAC banking clients, driving revenue through solution-oriented pitches and strong relationship management. I oversee cross-regional delivery teams (Singapore, India, China, and Malaysia), ensuring seamless execution and client satisfaction. With deep pre-sales and RFP expertise, I also mentor sales and pre-sales teams, while managing full P&L responsibilities to support sustainable business growth with a focus on value and profitability.

Skills: Stakeholder Management, New Business Development

PREVIOUS EXPERIENCE:

Senior Delivery Manager at FinTech Solutions
Aug 2009 - Sep 2017 (8 years 2 months)
Singapore · On-site, Full-time
As part of the core management team, successfully led multiple project deliveries, actively involved in pre-sales, sales, RFP responses, solutioning, and strategic planning for client engagements across ASIA clients

Skills: Project Delivery, Strategic Planning

Solutions Architect at TechBridge
May 2004 - Jul 2009 (5 years 3 months)
Singapore, Singapore · On-site, Full-time

EXPERTISE AREAS:
- Account Management and Client Engagement
- Project Management and Delivery
- Business Analysis
- Pre-Sales and RFP Expertise
- Cross-Regional Delivery Management (Singapore, India, China, Malaysia)
- Banking Technology Solutions
- P&L Management
- Team Mentoring and Leadership
- Solution-Oriented Selling
- Stakeholder Management
- Investment Banking Technology
- APAC Financial Services

KEY ACHIEVEMENTS:
- 16+ years of experience in investment banking technology
- Leads client engagement for major APAC banking clients at Nexora
- Manages cross-regional delivery teams across 4 countries
- Full P&L responsibility for APAC operations
- Strong track record in pre-sales, RFP responses, and strategic client engagements
- Deep expertise in Singapore and APAC financial markets""",
        metadata={
            "region": "Asia-Pacific",
            "location": "Singapore",
            "expertise": "Account Management, Project Delivery, Banking Technology, APAC",
            "reference_type": "nexora_team",
            "relationship": "Nexora Director - APAC Banking Clients",
        }
    )


def ingest_robert_clarke():
    """Ingest Robert Clarke's full profile"""
    return ingest_person_to_vector_store(
        person_name="Robert Clarke",
        title="Head of Derivatives Clearing & Clearing Risk Technology",
        company="National Securities Exchange",
        linkedin_url="https://www.linkedin.com/in/example-profile/",
        content="""Robert Clarke is the Head of Derivatives Clearing and Clearing Risk Technology at National Securities Exchange, based in Greater Sydney Area.

ABOUT:
Experienced technology professional with a solid track record of building and leading engineering teams delivering transformative tech change across multiple industries - primarily in financial services (Institutional Banking and Global Markets).

CURRENT ROLE:
Head of Derivatives Clearing and Clearing Risk Technology at National Securities Exchange
Aug 2023 - Present (2+ years)
Sydney, New South Wales, Australia
On-site, Full-time

EXPERIENCE AT PACIFIC TRUST BANK (PTB) - 6 years 3 months:

Executive Manager - Institutional Banking Technology
Sep 2021 - Aug 2023 (2 years)
Sydney, New South Wales, Australia

Executive Manager - Risk & Regulatory Technology, Global Markets
Aug 2019 - Sep 2021 (2 years 2 months)
Greater Sydney Area
Responsible for all traded risk and regulatory reporting, oversight and compliance/surveillance technology and associated program portfolio within Global Markets at PTB.

Program Manager - Global Markets
Jun 2017 - Jul 2019 (2 years 2 months)
Greater Sydney Area
- Successfully led large scale transformations within Global Markets
- Covered pre-trade risk simulations, market data, market RISK (FRTB), credit risk
- Led cross-disciplined teams of 50+ across core trading and data platform
- Industry leading AWS cloud implementation(s)

Program Manager - XVA System Implementation
Jul 2015 - 2017 (1 year 7 months)
Greater Sydney Area
- Overall program management for front-to-back implementation
- Pre-deal front office pricing + finance implementation of CVA/FVA
- New high performance computing technology platform
- Model validation
- New TradeSys 3.1 module covering 5 asset classes: Rates, FX, Commodities, Inflation & Credit

Project Manager, Structured Products & Derivatives, Institutional Banking & Markets
Mar 2014 - Jun 2015 (1 year 4 months)
- Integration & Reporting Lead on major derivatives programme
- Consolidating Interest Rate, FX, Fixed Income & Commodity products on TradeSys 3.1 platform

IT Project Manager, Customer Transformation Programme
Feb 2013 - Mar 2014 (1 year 2 months)
- Solution Centre Lead managing data migration & analytics deliverables
- PTB's Portfolio & Risk Management Customer Transformation Programme

Project Manager, Core Banking Modernisation
Nov 2010 - Jan 2013 (2 years 3 months)
- End-to-end test environment change and release management
- Core Banking Modernisation (CBM) programme

PREVIOUS EXPERIENCE:

Technology & Projects Manager at Pinnacle Staffing
May 2007 - Nov 2010 (3 years 7 months)
- Infrastructure & application projects for APAC region
- SCRUM master for local development team

Solutions Consultant at Telstra Corp (Govt & Enterprise)
2004 - 2007 (3 years)

EDUCATION:
- MBA, Technology & Finance - University of Technology Sydney (2005 - 2009)
- Bachelor Applied Sciences, Computer and Information Sciences - University of Sydney (1997 - 1999)

CERTIFICATIONS:
- Certified Professional - Australian Computer Society (Jul 2017)
- FNS51015 Diploma of Financial Markets (Debt Markets) - AFMA

EXPERTISE AREAS:
- Derivatives Clearing and Risk Technology
- Institutional Banking Technology
- Global Markets Technology
- Risk & Regulatory Technology (FRTB)
- XVA Systems (CVA/FVA)
- High Performance Computing
- TradeSys Platform Implementation
- AWS Cloud Implementation
- Large Scale Technology Transformation
- Team Leadership (50+ cross-disciplined teams)

KEY ACHIEVEMENTS:
- Led 45-person team delivering 18-month platform modernization at PTB
- Implemented industry-leading AWS cloud solutions for trading platforms
- Front-to-back XVA implementation across 5 asset classes
- Expert in trade finance digitization and system integration
- Transformed Global Markets technology at one of Australia's largest banks""",
        metadata={
            "region": "Australia",
            "location": "Sydney",
            "expertise": "Derivatives, Risk Technology, Global Markets, TradeSys",
            "reference_type": "credible_reference",
            "relationship": "Previous project sponsor - Trade Finance Platform at PTB",
        }
    )


if __name__ == "__main__":
    print("=" * 60)
    print("DealSense AI - Reference Data Ingestion (Full Profiles)")
    print("=" * 60)
    
    print("\n1. Ingesting Arjun Mehta profile...")
    try:
        ingest_arjun_mehta()
        print("   Done!")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Ingesting Thomas Blake profile...")
    try:
        ingest_thomas_blake()
        print("   Done!")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Ingesting Robert Clarke profile...")
    try:
        ingest_robert_clarke()
        print("   Done!")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Ingesting Omar Hassan profile...")
    try:
        ingest_omar_hassan()
        print("   Done!")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n5. Ingesting Vikram Patel profile...")
    try:
        ingest_vikram_patel()
        print("   Done!")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("Ingestion complete!")
    print("You can now query about these people in the chat:")
    print("  - 'Who is Arjun Mehta?'")
    print("  - 'Tell me about Thomas Blake from Eastern Commerce Bank'")
    print("  - 'What is Robert Clarke's experience at PTB?'")
    print("  - 'Who is Omar Hassan?'")
    print("  - 'Tell me about Vikram Patel'")
    print("=" * 60)
