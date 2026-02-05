import requests
import urllib.parse
from typing import List, Dict, Optional
from rich.console import Console

console = Console()

CROSSREF_API_URL = "https://api.crossref.org/works"

def validate_citations(citations: List[str]) -> List[Dict]:
    """
    Validate a list of citations against Crossref API.
    """
    results = []
    
    # Use a session for connection pooling
    session = requests.Session()
    session.headers.update({
        "User-Agent": "VeriCite/0.1.0 (mailto:hello@vericite.tools)"
    })

    for cit in citations:
        if not cit or len(cit.strip()) < 10:
            continue
            
        result = {
            "text": cit,
            "valid": False,
            "doi": None,
            "score": 0.0,
            "reason": "Not found"
        }

        try:
            # Query Crossref with the citation text
            # We use 'query.bibliographic' for free text search
            params = {
                "query.bibliographic": cit,
                "rows": 1,
                "select": "DOI,score,title,author"
            }
            
            resp = session.get(CROSSREF_API_URL, params=params, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("message", {}).get("items", [])
                
                if items:
                    top_match = items[0]
                    score = top_match.get("score", 0)
                    doi = top_match.get("DOI")
                    title = top_match.get("title", [""])[0]
                    
                    # Heuristic: Score needs to be reasonably high to be considered a match
                    # Note: Crossref scores are not normalized, but usually > 30-40 is decent for long text
                    # For MVP, we'll be lenient but mark it.
                    
                    result["doi"] = doi
                    result["score"] = score
                    result["matched_title"] = title
                    
                    # Basic validation logic: if we found a DOI and score is decent, we assume it exists.
                    # A "hallucination" typically returns NO results or completely irrelevant ones.
                    if score > 35.0: 
                        result["valid"] = True
                        result["reason"] = "Verified via Crossref"
                    else:
                        result["valid"] = False
                        result["reason"] = f"Low confidence match (Score: {score})"
                else:
                    result["reason"] = "No matching records found"
            else:
                result["reason"] = f"API Error {resp.status_code}"
                
        except Exception as e:
            result["reason"] = f"Network Error: {str(e)}"
            
        results.append(result)
        
    return results
