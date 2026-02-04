import ssl
import urllib.request
import json
import re

def web_search(query, max_results=5):
    """
    Search the web using DuckDuckGo HTML interface (no SSL issues).
    Falls back to a simple approach that works with older SSL libraries.
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
    
    # Fallback: Use DuckDuckGo's HTML lite version (works with older SSL)
    try:
        # Create SSL context that's more permissive
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # Use DuckDuckGo HTML lite which has simpler requirements
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(
            search_url,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        )
        
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            html = response.read().decode('utf-8')
            
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
        print(f"HTML search fallback failed: {e}")
    
    return ""
