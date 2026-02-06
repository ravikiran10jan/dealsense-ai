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


def ingest_vidyut_shetty():
    """Ingest Vidyut Shetty's full profile"""
    return ingest_person_to_vector_store(
        person_name="Vidyut Shetty",
        title="Head of A/NZ Banking and Capital Markets Solutions Sales",
        company="DXC Technology (DXC Luxoft)",
        linkedin_url="https://www.linkedin.com/in/vidyut-shetty/",
        content="""Vidyut Shetty is the Head of A/NZ Banking and Capital Markets Solutions Sales at DXC Technology, based in Greater Sydney Area.

ABOUT:
DXC Luxoft are an international consultancy specialising in Banking & Capital Markets technology with a focus on consulting, advisory, analytics, engineering and vendor platform integration.

With over 10,000 delivery consultants globally, delivering in a hybrid on/nearshore capacity, our services span Global Markets, Commodities, Asset & Wealth Management, Private Banking & Commercial/Institutional Banking.

We work with financial services organisations in the following domains:
- Global Markets / Investment Banking
- Asset Management / Hedge Funds / PE
- Wealth Management / Private Banking
- Commercial Banking
- Commodities (Physical & Derivatives)

Contact: vidyut.shetty@dxc.com

CURRENT ROLE:
DXC Banking and Capital Markets A/NZ Practice Lead at DXC Technology (Apr 2020 - Present, 5+ years)
Sydney, New South Wales, Australia

Using 20+ years' experience in hands-on delivery to help drive growth of Banking and Capital Markets consulting, analytics, vendor and engineering services businesses in the A/NZ region.

Skills: Operating Models, Sales Target Management, Business Development

EXPERIENCE AT EXCELIAN | LUXOFT FINANCIAL SERVICES (15+ years):

Director - Head of Vendor Solutions (Australia)
May 2018 - Present (7+ years)
Melbourne and Sydney Area, Australia

Head of Australia
May 2015 - Apr 2020 (5 years)
Greater Sydney Area
Director leading APAC business: Packaged Services (Murex, Calypso, Openlink) and Technical Consulting teams

Head of Technical Consulting & Delivery for Australia and Asia-Pacific
May 2010 - Oct 2017 (7+ years)
Melbourne and Sydney Area, Australia
- Principal Technical Consultant with responsibilities including sales, pre-sales, onsite consultancy and new business strategy
- Leading HPC, development and financial engineering team spread across Sydney and Melbourne
- Managing and expanding Excelian Australia and Asia Pacific technical consultancy business
- Specialising in High Performance Technologies: Data caching (Gemfire, Coherence), Grid Computing (Platform Symphony, Tibco DataSynapse, Microsoft HPC Server), High Frequency Trading Platforms (CEP, Apama)
- Development Services and Risk Systems (CCR, CVA, Market Risk, Operational Risk)
- Certified in MS HPC Server, IBM Platform and Tibco DataSynapse technologies
- On-site consultant leading teams delivering CCR/CVA solutions at banks in APAC region
- Building cloud solutions for financial companies using third-party data centre infrastructure
- Hosting CCR Community of Practice with leading Risk IT leaders

PREVIOUS EXPERIENCE:

Barclays Capital (3 years 2 months):
- Assistant Vice President: WebLogic Applications Grid Technical Lead (Dec 2008 - Oct 2009)
  - WebLogic Application Grid Architect: Oracle 11g WAG integration
  - Focus on Coherence and Oracle Enterprise Manager technologies
  - Project managing WebLogic and Data grid farm service using Oracle Coherence and DataSynapse
  - Architect for local and global data-grid solutions using Coherence
  - Put forward for Oracle 11g Application Grid Excellence Award
  - Architecting cloud HPC/data grid initiative

- HPC Grid Architect (Sep 2006 - Dec 2008)
  - Designing and implementing HPC and grid solutions across Barcap
  - DataSynapse engineer migrating grids across regions: London, New York, Singapore, Tokyo
  - HPC scavenging project saved bank over £X million
  - Part of IB team for Cloud computing solutions
  - Presented at Managing The Grid conference London 2008

UBS Investment Bank - Associate Director (Nov 2000 - Sep 2006, 5+ years)
- Team Leader of Global Service Delivery IRD Structured Products
- Implementing and supporting trade capture, risk management and pricing systems
- Managing team of 8 globally across New York, London, Singapore, Hong Kong

Credit Suisse - Intern (1999)

EXPERTISE AREAS:
- Banking & Capital Markets Technology
- Vendor Solutions (Murex, Calypso, Openlink)
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
            "email": "vidyut.shetty@dxc.com",
        }
    )


def ingest_ian_stephenson():
    """Ingest Ian Stephenson's full profile"""
    return ingest_person_to_vector_store(
        person_name="Ian Stephenson",
        title="CIO, Trade and Working Capital",
        company="Standard Chartered Bank",
        linkedin_url="https://www.linkedin.com/in/ianstephenson/",
        content="""Ian Stephenson is the CIO, Trade and Working Capital at Standard Chartered Bank, based in Singapore.

CURRENT ROLE:
CIO, Trade and Working Capital at Standard Chartered Bank
Feb 2024 - Present (2+ years)
Singapore
Full-time

EXPERIENCE AT STANDARD CHARTERED (10+ years):

MD - Global Head, FM Trade Processing and Post Trade Technology
Feb 2017 - Feb 2024 (7 years)
Singapore

MD - Global Head of Financial Markets Operations Technology
May 2015 - Feb 2017 (1 year 10 months)
Singapore

PREVIOUS EXPERIENCE:

Head of IT at SetClear (CLSA Group)
Jun 2010 - Apr 2015 (4 years 11 months)
Singapore

Head of Operations, South East Asia, Global Broker Services at GBST (Formally Coexis)
Aug 2008 - Jun 2010 (1 year 11 months)
Singapore

Lehman Brothers (8+ years):
- Head of Operations Technology Asia
- Head of IT South East Asia
- SVP
Jun 2000 - Aug 2008
Singapore

Associate Director at NatWest Markets Plc
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
- Experience across major financial institutions: Standard Chartered, Lehman Brothers, NatWest Markets
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


def ingest_andrew_marvin():
    """Ingest Andrew Marvin's full profile"""
    return ingest_person_to_vector_store(
        person_name="Andrew Marvin",
        title="Head of Derivatives Clearing & Clearing Risk Technology",
        company="ASX (Australian Securities Exchange)",
        linkedin_url="https://www.linkedin.com/in/andrew-marvin-2138799/",
        content="""Andrew Marvin is the Head of Derivatives Clearing and Clearing Risk Technology at ASX, based in Greater Sydney Area.

ABOUT:
Experienced technology professional with a solid track record of building and leading engineering teams delivering transformative tech change across multiple industries - primarily in financial services (Institutional Banking and Global Markets).

CURRENT ROLE:
Head of Derivatives Clearing and Clearing Risk Technology at ASX
Aug 2023 - Present (2+ years)
Sydney, New South Wales, Australia
On-site, Full-time

EXPERIENCE AT COMMONWEALTH BANK (CBA) - 6 years 3 months:

Executive Manager - Institutional Banking Technology
Sep 2021 - Aug 2023 (2 years)
Sydney, New South Wales, Australia

Executive Manager - Risk & Regulatory Technology, Global Markets
Aug 2019 - Sep 2021 (2 years 2 months)
Greater Sydney Area
Responsible for all traded risk and regulatory reporting, oversight and compliance/surveillance technology and associated program portfolio within Global Markets at CBA.

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
- New Murex 3.1 module covering 5 asset classes: Rates, FX, Commodities, Inflation & Credit

Project Manager, Structured Products & Derivatives, Institutional Banking & Markets
Mar 2014 - Jun 2015 (1 year 4 months)
- Integration & Reporting Lead on major derivatives programme
- Consolidating Interest Rate, FX, Fixed Income & Commodity products on Murex 3.1 platform

IT Project Manager, Customer Transformation Programme
Feb 2013 - Mar 2014 (1 year 2 months)
- Solution Centre Lead managing data migration & analytics deliverables
- CBA's Portfolio & Risk Management Customer Transformation Programme

Project Manager, Core Banking Modernisation
Nov 2010 - Jan 2013 (2 years 3 months)
- End-to-end test environment change and release management
- Core Banking Modernisation (CBM) programme

PREVIOUS EXPERIENCE:

Technology & Projects Manager at Hays
May 2007 - Nov 2010 (3 years 7 months)
- Infrastructure & application projects for APAC region
- SCRUM master for local development team

Solutions Consultant at Optus (Govt & Enterprise)
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
- Murex Platform Implementation
- AWS Cloud Implementation
- Large Scale Technology Transformation
- Team Leadership (50+ cross-disciplined teams)

KEY ACHIEVEMENTS:
- Led 45-person team delivering 18-month platform modernization at CBA
- Implemented industry-leading AWS cloud solutions for trading platforms
- Front-to-back XVA implementation across 5 asset classes
- Expert in trade finance digitization and system integration
- Transformed Global Markets technology at one of Australia's largest banks""",
        metadata={
            "region": "Australia",
            "location": "Sydney",
            "expertise": "Derivatives, Risk Technology, Global Markets, Murex",
            "reference_type": "credible_reference",
            "relationship": "Previous project sponsor - Trade Finance Platform at CBA",
        }
    )


if __name__ == "__main__":
    print("=" * 60)
    print("DealSense AI - Reference Data Ingestion (Full Profiles)")
    print("=" * 60)
    
    print("\n1. Ingesting Vidyut Shetty profile...")
    try:
        ingest_vidyut_shetty()
        print("   Done!")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Ingesting Ian Stephenson profile...")
    try:
        ingest_ian_stephenson()
        print("   Done!")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Ingesting Andrew Marvin profile...")
    try:
        ingest_andrew_marvin()
        print("   Done!")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("Ingestion complete!")
    print("You can now query about these people in the chat:")
    print("  - 'Who is Vidyut Shetty?'")
    print("  - 'Tell me about Ian Stephenson from Standard Chartered'")
    print("  - 'What is Andrew Marvin's experience at CBA?'")
    print("=" * 60)
