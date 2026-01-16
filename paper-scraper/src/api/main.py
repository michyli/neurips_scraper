"""
FastAPI backend for paper scraper
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers import ConferenceScraper, ACLScraper

app = FastAPI(
    title="Paper Scraper API",
    description="API for searching academic papers from AI/ML/NLP conferences",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scrapers
openreview_scraper = ConferenceScraper()
acl_scraper = ACLScraper()

# Conference configurations
CONFERENCES = {
    "neurips": {"type": "openreview", "name": "NeurIPS", "full_name": "Neural Information Processing Systems"},
    "icml": {"type": "openreview", "name": "ICML", "full_name": "International Conference on Machine Learning"},
    "iclr": {"type": "openreview", "name": "ICLR", "full_name": "International Conference on Learning Representations"},
    "acl": {"type": "acl", "name": "ACL", "full_name": "Association for Computational Linguistics"},
    "emnlp": {"type": "acl", "name": "EMNLP", "full_name": "Empirical Methods in Natural Language Processing"},
    "naacl": {"type": "acl", "name": "NAACL", "full_name": "North American Chapter of the ACL"},
    "eacl": {"type": "acl", "name": "EACL", "full_name": "European Chapter of the ACL"},
    "coling": {"type": "acl", "name": "COLING", "full_name": "International Conference on Computational Linguistics"},
}


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Paper Scraper API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/conferences")
def list_conferences():
    """List all supported conferences"""
    return {
        "conferences": [
            {
                "id": conf_id,
                "name": conf["name"],
                "full_name": conf["full_name"],
                "type": conf["type"]
            }
            for conf_id, conf in CONFERENCES.items()
        ]
    }


@app.get("/papers/{conference}/{year}")
def get_papers(
    conference: str,
    year: int,
    limit: int = Query(default=10, ge=1, le=100),
    search: Optional[str] = None
):
    """
    Get papers from a specific conference and year
    
    Args:
        conference: Conference ID (e.g., 'neurips', 'acl')
        year: Conference year
        limit: Maximum number of papers to return
        search: Optional search query to filter papers
    """
    if conference not in CONFERENCES:
        raise HTTPException(
            status_code=404,
            detail=f"Conference '{conference}' not found. Available: {list(CONFERENCES.keys())}"
        )
    
    conf_info = CONFERENCES[conference]
    
    try:
        # Fetch papers based on conference type
        if conf_info["type"] == "openreview":
            papers = openreview_scraper.get_conference_papers(
                conference,
                year,
                limit=limit
            )
            # Extract and normalize paper info
            papers = [
                openreview_scraper.extract_paper_info(paper, conference=conf_info["name"])
                for paper in papers
            ]
        else:  # ACL
            papers = acl_scraper.get_conference_papers(
                conference,
                year,
                limit=limit
            )
        
        # Apply search filter if provided
        if search and papers:
            search_lower = search.lower()
            papers = [
                p for p in papers
                if (search_lower in p.get('title', '').lower() or
                    search_lower in p.get('abstract', '').lower() or
                    any(search_lower in author.lower() for author in p.get('authors', [])))
            ]
        
        return {
            "conference": conference,
            "conference_name": conf_info["name"],
            "year": year,
            "count": len(papers),
            "papers": papers
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching papers: {str(e)}"
        )


@app.get("/search")
def search_papers(
    q: str = Query(..., min_length=1),
    conference: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    Search papers across conferences
    
    Args:
        q: Search query
        conference: Optional conference filter
        year: Optional year filter
        limit: Maximum number of results
    """
    # For MVP, we'll do a simple search across recent papers
    # In production, this would query a database
    
    results = []
    conferences_to_search = [conference] if conference else ["neurips", "icml", "acl"]
    search_year = year or 2024
    
    for conf in conferences_to_search:
        if conf in CONFERENCES:
            try:
                papers_data = get_papers(conf, search_year, limit=50, search=q)
                results.extend(papers_data["papers"])
            except:
                continue
    
    # Limit results
    results = results[:limit]
    
    return {
        "query": q,
        "count": len(results),
        "papers": results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
