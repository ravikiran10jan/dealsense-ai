"""
RAG-based Credible References Retrieval

Retrieves credible reference contacts from the vector database
based on deal context and industry.
"""
from typing import List, Dict, Any
from retrieval.semantic_search import semantic_search_with_scores


def get_credible_references(
    industry: str = "",
    description: str = "",
    max_references: int = 2
) -> List[Dict[str, Any]]:
    """
    Retrieve credible references from the vector database.
    
    Searches for person profiles that match the deal context
    and returns formatted reference data.
    
    Args:
        industry: Client's industry for relevance matching
        description: Deal description for context
        max_references: Maximum number of references to return
    
    Returns:
        List of reference dictionaries with name, company, role, relationship, linkedin_url
    """
    # Build query to find relevant person profiles
    query = f"credible reference contact trade finance banking {industry} {description}"
    
    try:
        # Search with higher k to find person profiles
        results = semantic_search_with_scores(query, k=10)
        
        references = []
        seen_names = set()
        
        for doc, score in results:
            # Only include person_profile types
            if doc.metadata.get("type") != "person_profile":
                continue
            
            # Skip if we've already added this person
            person_name = doc.metadata.get("person_name", "")
            if person_name in seen_names:
                continue
            
            seen_names.add(person_name)
            
            # Extract reference info from metadata
            reference = {
                "name": person_name,
                "company": doc.metadata.get("company", ""),
                "role": doc.metadata.get("title", ""),
                "relationship": doc.metadata.get("relationship", "Industry expert"),
                "linkedin_url": doc.metadata.get("linkedin_url", ""),
            }
            
            references.append(reference)
            
            if len(references) >= max_references:
                break
        
        return references
        
    except Exception as e:
        print(f"Error retrieving credible references: {e}")
        return []


def get_credible_references_for_deal(
    account_name: str,
    industry: str,
    description: str,
    max_references: int = 2
) -> List[Dict[str, Any]]:
    """
    Get credible references specifically tailored for a deal.
    
    Args:
        account_name: Name of the client/account
        industry: Client's industry
        description: Deal description
        max_references: Maximum references to return
    
    Returns:
        List of reference dictionaries
    """
    references = get_credible_references(
        industry=industry,
        description=description,
        max_references=max_references
    )
    
    # If no references found from RAG, return empty list
    # (the caller can decide to use fallback)
    return references
