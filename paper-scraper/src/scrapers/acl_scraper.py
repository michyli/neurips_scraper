#!/usr/bin/env python3
"""
ACL Anthology Paper Scraper
Scrapes papers from ACL, EMNLP, NAACL, and other ACL Anthology venues
"""

import requests
import re
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ACL Anthology venue configurations
ACL_VENUES = {
    'acl': {
        'name': 'ACL',
        'full_name': 'Annual Meeting of the Association for Computational Linguistics',
        'volumes': ['long', 'short']
    },
    'emnlp': {
        'name': 'EMNLP',
        'full_name': 'Empirical Methods in Natural Language Processing',
        'volumes': ['long', 'short']
    },
    'naacl': {
        'name': 'NAACL',
        'full_name': 'North American Chapter of the ACL',
        'volumes': ['long', 'short']
    },
    'eacl': {
        'name': 'EACL',
        'full_name': 'European Chapter of the ACL',
        'volumes': ['long', 'short']
    },
    'coling': {
        'name': 'COLING',
        'full_name': 'International Conference on Computational Linguistics',
        'volumes': ['long', 'short']
    }
}


class ACLScraper:
    """Scraper for ACL Anthology papers"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
        self.base_url = "https://aclanthology.org"
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.3  # 300ms between requests
        
        logger.info(f"Initialized ACLScraper with base_url={self.base_url}")
    
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get_paper_ids_from_event(self, venue: str, year: int) -> List[str]:
        """
        Get all paper IDs from a conference event page
        
        Args:
            venue: Venue name (e.g., 'acl', 'emnlp')
            year: Conference year
            
        Returns:
            List of paper IDs
        """
        url = f"{self.base_url}/events/{venue}-{year}/"
        logger.info(f"Fetching paper list from: {url}")
        
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            paper_ids = []
            
            # Find all links matching paper ID pattern
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Pattern: /YEAR.venue-track.number/
                match = re.match(r'^/(\d{4}\.[a-z-]+\.\d+)/$', href)
                if match:
                    paper_ids.append(match.group(1))
            
            # Remove duplicates while preserving order
            paper_ids = list(dict.fromkeys(paper_ids))
            logger.info(f"Found {len(paper_ids)} papers for {venue.upper()} {year}")
            return paper_ids
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Event page not found: {url}")
            else:
                logger.error(f"HTTP error fetching event page: {e}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching event page: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing event page: {e}")
            return []
    
    def get_paper_bibtex(self, paper_id: str) -> Optional[str]:
        """
        Fetch BibTeX entry for a paper
        
        Args:
            paper_id: Paper ID (e.g., '2024.acl-long.1')
            
        Returns:
            BibTeX string or None
        """
        url = f"{self.base_url}/{paper_id}.bib"
        logger.debug(f"Fetching BibTeX: {url}")
        
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching BibTeX for {paper_id}: {e}")
            return None
    
    def parse_bibtex(self, bibtex: str) -> Dict:
        """
        Parse BibTeX string into structured data
        
        Args:
            bibtex: BibTeX string
            
        Returns:
            Dictionary with parsed fields
        """
        result = {}
        
        try:
            # Extract title
            title_match = re.search(r'title\s*=\s*["{](.*?)["}]', bibtex, re.DOTALL)
            if title_match:
                result['title'] = title_match.group(1).strip()
            
            # Extract authors
            author_match = re.search(r'author\s*=\s*["{](.*?)["}]', bibtex, re.DOTALL)
            if author_match:
                authors_str = author_match.group(1)
                # Split by 'and' and clean up
                authors = [a.strip() for a in authors_str.split(' and ')]
                result['authors'] = authors
                result['raw_authors'] = authors  # Same for ACL
            
            # Extract year
            year_match = re.search(r'year\s*=\s*["{]?(\d{4})["}]?', bibtex)
            if year_match:
                result['year'] = int(year_match.group(1))
            
            # Extract booktitle (conference name)
            booktitle_match = re.search(r'booktitle\s*=\s*["{](.*?)["}]', bibtex, re.DOTALL)
            if booktitle_match:
                result['booktitle'] = booktitle_match.group(1).strip()
            
            # Extract pages
            pages_match = re.search(r'pages\s*=\s*["{](\d+)--(\d+)["}]', bibtex)
            if pages_match:
                result['pages'] = f"{pages_match.group(2)}-{pages_match.group(1)}"
            
            # Extract DOI
            doi_match = re.search(r'doi\s*=\s*["{](.*?)["}]', bibtex)
            if doi_match:
                result['doi'] = doi_match.group(1).strip()
            
            # Extract URL
            url_match = re.search(r'url\s*=\s*["{](.*?)["}]', bibtex)
            if url_match:
                result['url'] = url_match.group(1).strip()
            
        except Exception as e:
            logger.error(f"Error parsing BibTeX: {e}")
        
        return result
    
    def get_paper_html(self, paper_id: str) -> Optional[Dict]:
        """
        Scrape paper details from HTML page
        
        Args:
            paper_id: Paper ID (e.g., '2024.acl-long.1')
            
        Returns:
            Dictionary with paper details
        """
        url = f"{self.base_url}/{paper_id}/"
        logger.debug(f"Fetching paper page: {url}")
        
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            result = {}
            
            # Extract abstract
            abstract_div = soup.find('div', class_='abstract')
            if abstract_div:
                # Get the span with the actual abstract text
                abstract_span = abstract_div.find('span', class_='abstract-full')
                if abstract_span:
                    result['abstract'] = abstract_span.get_text().strip()
                else:
                    result['abstract'] = abstract_div.get_text().strip()
            
            # Extract PDF URL
            pdf_link = soup.find('a', class_='badge-primary', href=re.compile(r'\.pdf$'))
            if pdf_link and 'href' in pdf_link.attrs:
                result['pdf_url'] = pdf_link['href']
                if not result['pdf_url'].startswith('http'):
                    result['pdf_url'] = self.base_url + result['pdf_url']
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching paper page for {paper_id}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error parsing paper page for {paper_id}: {e}")
            return {}
    
    def get_paper_info(self, paper_id: str) -> Optional[Dict]:
        """
        Get complete paper information by combining BibTeX and HTML data
        
        Args:
            paper_id: Paper ID (e.g., '2024.acl-long.1')
            
        Returns:
            Complete paper information dictionary
        """
        logger.info(f"Fetching complete info for paper: {paper_id}")
        
        # Get BibTeX data
        bibtex = self.get_paper_bibtex(paper_id)
        if not bibtex:
            logger.warning(f"Could not fetch BibTeX for {paper_id}")
            return None
        
        # Parse BibTeX
        paper_info = self.parse_bibtex(bibtex)
        paper_info['id'] = paper_id
        paper_info['bibtex'] = bibtex
        
        # Get HTML data for abstract and PDF URL
        html_data = self.get_paper_html(paper_id)
        if html_data:
            paper_info.update(html_data)
        
        # Add ACL Anthology URLs
        paper_info['anthology_url'] = f"{self.base_url}/{paper_id}/"
        if 'pdf_url' not in paper_info:
            paper_info['pdf_url'] = f"{self.base_url}/{paper_id}.pdf"
        
        # Add timestamps
        paper_info['scraped_time'] = datetime.now().isoformat()
        
        return paper_info
    
    def _filter_papers(self, papers: List[Dict], search_query: str) -> List[Dict]:
        """
        Filter papers by search query (case-insensitive search in title, abstract, authors)
        
        Args:
            papers: List of paper dictionaries
            search_query: Search string
            
        Returns:
            Filtered list of papers
        """
        if not search_query:
            return papers
        
        search_lower = search_query.lower()
        filtered = []
        
        for paper in papers:
            try:
                # Search in title
                if search_lower in paper.get('title', '').lower():
                    filtered.append(paper)
                    continue
                
                # Search in abstract
                if search_lower in paper.get('abstract', '').lower():
                    filtered.append(paper)
                    continue
                
                # Search in authors
                authors = paper.get('authors', [])
                if any(search_lower in author.lower() for author in authors):
                    filtered.append(paper)
                    continue
                    
            except (AttributeError, TypeError):
                continue
        
        return filtered
    
    def get_conference_papers(self, venue: str, year: int, limit: Optional[int] = None, search_query: Optional[str] = None) -> List[Dict]:
        """
        Get all papers from a conference with optional search filtering
        
        Args:
            venue: Venue name (e.g., 'acl', 'emnlp')
            year: Conference year
            limit: Maximum number of papers to fetch (None for all)
            search_query: Optional search query to filter papers by title/abstract/authors
            
        Returns:
            List of paper dictionaries
        """
        paper_ids = self.get_paper_ids_from_event(venue, year)
        
        if not paper_ids:
            logger.warning(f"No papers found for {venue.upper()} {year}")
            return []
        
        # If we have a search query, fetch more papers to ensure we get enough matches
        fetch_limit = limit
        if search_query and limit:
            fetch_limit = min(limit * 2, len(paper_ids))  # Fetch 2x limit or all available
            logger.info(f"Search query provided, fetching {fetch_limit} papers for filtering")
        elif limit:
            fetch_limit = limit
            logger.info(f"Limiting to {limit} papers")
        
        # Fetch papers
        papers = []
        fetch_count = fetch_limit if fetch_limit else len(paper_ids)
        for i, paper_id in enumerate(paper_ids[:fetch_count], 1):
            logger.info(f"Fetching paper {i}/{fetch_count}: {paper_id}")
            paper_info = self.get_paper_info(paper_id)
            if paper_info:
                papers.append(paper_info)
        
        # Apply search filter if provided
        if search_query:
            papers = self._filter_papers(papers, search_query)
            logger.info(f"After filtering: {len(papers)} papers match query '{search_query}'")
        
        # Apply limit after filtering
        if limit and len(papers) > limit:
            papers = papers[:limit]
        
        return papers


def main():
    """Demo usage for ACL scraper"""
    scraper = ACLScraper()
    
    # Test with ACL 2024
    print("="*80)
    print("Testing ACL Anthology Scraper - ACL 2024")
    print("="*80)
    print()
    
    # Fetch first 3 papers
    papers = scraper.get_conference_papers('acl', 2024, limit=3)
    
    print(f"\nFound {len(papers)} papers\n")
    
    for i, paper in enumerate(papers, 1):
        print(f"Paper {i}:")
        print(f"  ID: {paper.get('id')}")
        print(f"  Title: {paper.get('title')}")
        print(f"  Authors: {', '.join(paper.get('authors', [])[:3])}...")
        print(f"  Year: {paper.get('year')}")
        print(f"  Abstract: {paper.get('abstract', 'N/A')[:100]}...")
        print(f"  PDF: {paper.get('pdf_url')}")
        print(f"  URL: {paper.get('anthology_url')}")
        print()
    
    # Save first paper
    if papers:
        import json
        with open('sample_acl_paper.json', 'w', encoding='utf-8') as f:
            json.dump(papers[0], f, indent=2, ensure_ascii=False)
        print("Sample paper saved to sample_acl_paper.json")


if __name__ == "__main__":
    main()

