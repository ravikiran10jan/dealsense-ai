import urllib.parse
import re

def web_search(query, max_results=5):
    """
    Search the web using DuckDuckGo HTML interface.
    Uses proper SSL verification for security.
    """
    results = []
    
    # First try the ddgs package
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                body = r.get("body", "")
                if body:
                    results.append(body)
        
        if results:
            return "\n".join(results)
    except Exception as e:
        print(f"DDGS search failed: {e}")
    
    # Fallback: Use httpx library with proper SSL verification
    try:
        import httpx
        
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        
        with httpx.Client(timeout=10.0, verify=True) as client:
            response = client.get(
                search_url,
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            )
            response.raise_for_status()
        
        html = response.text
        
        # Extract result snippets from HTML
        # DuckDuckGo HTML results are in <a class="result__snippet"> tags
        snippet_pattern = r'class="result__snippet"[^>]*>([^<]+)<'
        snippets = re.findall(snippet_pattern, html)
        
        for snippet in snippets[:max_results]:
            # Clean up the snippet
            clean_snippet = snippet.strip()
            if clean_snippet and len(clean_snippet) > 20:
                results.append(clean_snippet)
        
        if results:
            return "\n".join(results)
            
    except Exception as e:
        if "SSL" in str(e) or "certificate" in str(e).lower():
            # Log SSL errors but don't bypass verification
            print(f"SSL verification failed for web search: {e}")
            print("Web search unavailable due to SSL issues. Skipping.")
        else:
            print(f"HTML search fallback failed: {e}")
    
    return ""
