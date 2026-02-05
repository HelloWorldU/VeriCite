import fitz  # PyMuPDF
import re

def smart_slice(pdf_path: str) -> int:
    """
    Identify the page number where References start.
    Returns 0-based index, or -1 if not found.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return -1

    # Regex patterns for common section headers
    # Case insensitive, optional numbering (e.g. "12. References")
    patterns = [
        r"^\s*(?:[0-9]+\.?\s*)?References\s*$",
        r"^\s*(?:[0-9]+\.?\s*)?Bibliography\s*$",
        r"^\s*(?:[0-9]+\.?\s*)?Works Cited\s*$",
        r"^\s*(?:[0-9]+\.?\s*)?参考文献\s*$",
        r"^\s*(?:[0-9]+\.?\s*)?LITERATURE CITED\s*$"
    ]
    
    combined_pattern = re.compile("|".join(patterns), re.IGNORECASE | re.MULTILINE)
    
    # Strategy 1: Check Table of Contents (Outline)
    # This is the fastest method if TOC exists
    toc = doc.get_toc()
    for entry in toc:
        # entry format: [lvl, title, page, dest]
        title = entry[1]
        if combined_pattern.search(title):
            # PyMuPDF TOC pages are 1-based, convert to 0-based
            return max(0, entry[2] - 1)

    # Strategy 2: Heuristic Scan (Last 20% of pages)
    total_pages = len(doc)
    start_check = max(0, int(total_pages * 0.8))
    
    # We iterate backwards from the end? No, forward from 80% mark makes sense for "References"
    # But sometimes References are followed by Appendix.
    
    for i in range(start_check, total_pages):
        text = doc[i].get_text("text") # plain text
        # Look for the header pattern in the first few lines of the page usually
        # But simply searching the whole page text is safer for MVP
        if combined_pattern.search(text):
            return i
            
    # Strategy 3: Full Scan (if not found in end)
    # Sometimes references are earlier (e.g. conference papers with appendices)
    for i in range(start_check):
        text = doc[i].get_text()
        if combined_pattern.search(text):
            return i
                
    return -1
