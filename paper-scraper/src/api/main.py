"""
FastAPI backend for paper scraper
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import sys
import os
import hashlib
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers import ConferenceScraper, ACLScraper

app = FastAPI(
    title="Paper Scraper API",
    description="API for searching academic papers from AI/ML/NLP conferences",
    version="0.1.0"
)

# Configure CORS
# WARNING: For production, restrict origins to your actual frontend domain
# Example: allow_origins=["https://neurips.aipapertrails.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Initialize scrapers
openreview_scraper = ConferenceScraper()
acl_scraper = ACLScraper()

# Simple in-memory cache for API responses
# Format: {cache_key: {"data": response, "timestamp": time}}
api_cache = {}
CACHE_TTL = 300  # 5 minutes cache

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


def get_cache_key(*args) -> str:
    """Generate cache key from arguments"""
    key_string = "_".join(str(arg) for arg in args if arg is not None)
    return hashlib.md5(key_string.encode()).hexdigest()


def get_from_cache(cache_key: str):
    """Get data from cache if valid"""
    if cache_key in api_cache:
        cached = api_cache[cache_key]
        if time.time() - cached["timestamp"] <= CACHE_TTL:
            return cached["data"]
        else:
            # Remove expired entry
            del api_cache[cache_key]
    return None


def save_to_cache(cache_key: str, data):
    """Save data to cache"""
    api_cache[cache_key] = {
        "data": data,
        "timestamp": time.time()
    }


FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


@app.get("/")
def root():
    """Serve the main frontend page"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "Paper Scraper API", "version": "0.1.0", "docs": "/docs"}


@app.get("/visualize")
def visualize():
    """Serve the 3D visualization page"""
    viz_path = os.path.join(FRONTEND_DIR, "visualize.html")
    if os.path.exists(viz_path):
        return FileResponse(viz_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Visualization page not found")


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
    limit: int = Query(default=10, ge=1, le=10000),  # Increased max to 10,000
    search: Optional[str] = None,
    fetch_all: bool = Query(default=False, description="Fetch all papers (ignores limit)")
):
    """
    Get papers from a specific conference and year
    
    Args:
        conference: Conference ID (e.g., 'neurips', 'acl')
        year: Conference year
        limit: Maximum number of papers to return (max 10,000, or use fetch_all=true)
        search: Optional search query to filter papers
        fetch_all: If true, fetches all papers from the conference (ignores limit)
    """
    if conference not in CONFERENCES:
        raise HTTPException(
            status_code=404,
            detail=f"Conference '{conference}' not found. Available: {list(CONFERENCES.keys())}"
        )
    
    # Check cache first
    cache_key = get_cache_key(conference, year, limit, search, fetch_all)
    cached_result = get_from_cache(cache_key)
    if cached_result is not None:
        return cached_result
    
    conf_info = CONFERENCES[conference]
    
    # Add logging imports if not present
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Fetch papers based on conference type
        # Search filtering is now done at scraper level for better performance
        mode = "ALL PAPERS" if fetch_all else f"{limit} papers"
        logger.info(f"📥 Starting request: {conference.upper()} {year} ({mode})")
        
        if conf_info["type"] == "openreview":
            logger.info(f"🔍 Fetching from OpenReview API...")
            papers = openreview_scraper.get_conference_papers(
                conference,
                year,
                limit=limit,
                fetch_all=fetch_all,  # Pass fetch_all parameter
                search_query=search  # Pass search to scraper for efficient filtering
            )
            # Extract and normalize paper info
            logger.info(f"📝 Processing {len(papers)} papers (extracting info)...")
            papers = [
                openreview_scraper.extract_paper_info(paper, conference=conf_info["name"])
                for paper in papers
            ]
            logger.info(f"✓ Extraction complete!")
        else:  # ACL
            logger.info(f"🔍 Fetching from ACL Anthology...")
            # For ACL, if fetch_all is True, pass None as limit
            acl_limit = None if fetch_all else limit
            papers = acl_scraper.get_conference_papers(
                conference,
                year,
                limit=acl_limit,
                search_query=search  # Pass search to scraper for efficient filtering
            )
            logger.info(f"✓ ACL fetch complete!")
        
        result = {
            "conference": conference,
            "conference_name": conf_info["name"],
            "year": year,
            "count": len(papers),
            "papers": papers
        }
        
        # Save to cache
        save_to_cache(cache_key, result)
        logger.info(f"✅ REQUEST COMPLETE: Returning {len(papers)} papers for {conference.upper()} {year}")
        return result
        
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
    limit: int = Query(default=100, ge=1, le=500)
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

