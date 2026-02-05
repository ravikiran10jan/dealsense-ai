"""
RAG-based Suggested Talking Points Generation

Uses semantic search to retrieve relevant context about similar deals,
then generates tailored talking points using LLM.
"""
import os
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Lazy initialization of LLM
_llm = None


def get_llm():
    """Get or initialize the LLM client (lazy loading)."""
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,  # Slightly higher for more creative talking points
            api_key=os.getenv("OPENAI_API_KEY")
        )
    return _llm


def generate_talking_points(
    client_name: str,
    industry: str,
    description: str,
    rag_context: str,
    num_points: int = 4
) -> List[str]:
    """
    Generate suggested talking points based on client context and RAG-retrieved information.
    
    Args:
        client_name: Name of the client/account
        industry: Client's industry
        description: Deal description or focus area
        rag_context: Context retrieved from vector database (similar deals, case studies)
        num_points: Number of talking points to generate (default 4)
    
    Returns:
        List of talking points as strings
    """
    prompt = f"""You are a sales assistant helping prepare talking points for a client meeting.

CLIENT INFORMATION:
- Client Name: {client_name}
- Industry: {industry}
- Focus Area: {description}

RELEVANT CONTEXT FROM KNOWLEDGE BASE:
{rag_context if rag_context else "No specific context available."}

INSTRUCTIONS:
Generate exactly {num_points} concise, impactful talking points for the upcoming call with {client_name}.

Each talking point should:
1. Be specific and data-driven when possible (include numbers, timelines, percentages)
2. Reference relevant case studies or similar implementations from the context
3. Address likely concerns for their industry ({industry})
4. Be formatted as a single line, ready to use in conversation

Format: Return ONLY the talking points, one per line, without numbering or bullet points.

Example format:
CBA implementation: 45-person team, 18-month timeline with zero downtime
SMBC: Integrated 3 core systems + SWIFT connectivity in 12 months
SCB: Singapore-only rollout ensured data privacy compliance
AI document classification: 92% accuracy in production POC

Generate talking points now:"""

    try:
        response = get_llm().invoke(prompt)
        content = response.content.strip()
        
        # Parse response into list of talking points
        points = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Ensure we have the requested number of points
        if len(points) > num_points:
            points = points[:num_points]
        
        return points
    except Exception as e:
        print(f"Error generating talking points: {e}")
        # Return fallback talking points
        return [
            f"Discuss {description} implementation approach with {client_name}",
            f"Reference similar {industry} implementations",
            "Highlight team expertise and delivery methodology",
            "Address data privacy and compliance requirements",
        ]


def generate_talking_points_from_query(
    client_name: str,
    industry: str,
    description: str,
    semantic_search_fn,
    num_points: int = 4
) -> Dict[str, Any]:
    """
    End-to-end talking points generation: retrieves context via RAG, then generates points.
    
    Args:
        client_name: Name of the client/account
        industry: Client's industry  
        description: Deal description or focus area
        semantic_search_fn: Function to call for semantic search (injected dependency)
        num_points: Number of talking points to generate
    
    Returns:
        Dict with 'talking_points' list and 'sources' list
    """
    # Build query for relevant context
    query = f"Similar {industry} implementations case studies for {description} with team size timeline outcomes"
    
    sources = []
    rag_context = ""
    
    try:
        # Retrieve relevant documents
        results = semantic_search_fn(query, k=5)
        
        if results:
            # Build context from retrieved documents
            context_parts = []
            for doc in results:
                content = doc.page_content[:500]  # Limit each doc
                source = doc.metadata.get("source", "Unknown")
                context_parts.append(f"[{source}]: {content}")
                if source not in sources:
                    sources.append(source)
            
            rag_context = "\n\n".join(context_parts)
    except Exception as e:
        print(f"Error in semantic search: {e}")
    
    # Generate talking points
    talking_points = generate_talking_points(
        client_name=client_name,
        industry=industry,
        description=description,
        rag_context=rag_context,
        num_points=num_points
    )
    
    return {
        "talking_points": talking_points,
        "sources": sources,
        "source_type": "RAG+LLM" if rag_context else "LLM"
    }
