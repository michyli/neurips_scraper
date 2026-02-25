#!/usr/bin/env python3
"""
Generic Conference Paper Scraper
Works with OpenReview-based conferences (NeurIPS, ICML, ICLR, etc.)
"""

import requests
import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Conference venue ID configurations
CONFERENCE_VENUES = {
    'neurips': {
        'name': 'NeurIPS',
        'venue_template': 'NeurIPS.cc/{year}/Conference',
        'years': [2024, 2023, 2022, 2021]
    },
    'icml': {
        'name': 'ICML',
        'venue_template': 'ICML.cc/{year}/Conference',
        'years': [2024, 2023, 2022, 2021]
    },
    'iclr': {
        'name': 'ICLR',
        'venue_template': 'ICLR.cc/{year}/Conference',
        'years': [2024, 2023, 2022, 2021]
    }
}


class ConferenceScraper:
    """Generic scraper for OpenReview-based conferences"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
        self.base_url = "https://api2.openreview.net"
        self.session = requests.Session()
        self._cache = {}  # Simple in-memory cache for repeated queries
        
        # Configure retry strategy for rate limiting and transient errors
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests
        
        logger.info(f"Initialized ConferenceScraper with base_url={self.base_url}")
    
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get_venue_id(self, conference: str, year: int) -> Optional[str]:
        """
        Get OpenReview venue ID for a conference and year
        
        Args:
            conference: Conference name (e.g., 'neurips', 'icml')
            year: Conference year
            
        Returns:
            Venue ID string or None if not found
        """
        conference_lower = conference.lower()
        if conference_lower not in CONFERENCE_VENUES:
            logger.error(f"Unknown conference: {conference}")
            return None
        
        config = CONFERENCE_VENUES[conference_lower]
        venue_id = config['venue_template'].format(year=year)
        logger.info(f"Generated venue ID: {venue_id}")
        return venue_id
    
    def get_venue_submissions(self, venue_id: str, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        Fetch submissions for a given venue (conference)
        
        Args:
            venue_id: OpenReview venue ID (e.g., 'NeurIPS.cc/2024/Conference')
            limit: Maximum number of papers to fetch
            offset: Offset for pagination
            
        Returns:
            List of paper dictionaries
        """
        logger.info(f"Fetching submissions for venue: {venue_id}, limit: {limit}, offset: {offset}")
        url = f"{self.base_url}/notes"
        params = {
            'invitation': f'{venue_id}/-/Submission',
            'details': 'replyCount,invitation,original',
            'limit': limit,
            'offset': offset
        }
        
        try:
            self._rate_limit()
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            papers = data.get('notes', [])
            logger.info(f"Successfully fetched {len(papers)} papers from {venue_id}")
            return papers
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error(f"Rate limit exceeded for {venue_id}: {e}")
                logger.info("Consider increasing min_request_interval or adding exponential backoff")
            else:
                logger.error(f"HTTP error fetching submissions from {venue_id}: {e}")
            return []
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {venue_id}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching submissions from {venue_id}: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from {venue_id}: {e}")
            return []
    
    def get_conference_papers(self, conference: str, year: int, limit: int = 100, fetch_all: bool = False, search_query: Optional[str] = None) -> List[Dict]:
        """
        Fetch papers from a conference year with optional search filtering
        
        Args:
            conference: Conference name (e.g., 'neurips', 'icml')
            year: Conference year
            limit: Maximum total number of papers to fetch (default 100)
            fetch_all: If True, fetch all papers ignoring limit
            search_query: Optional search query to filter papers by title/abstract/authors
            
        Returns:
            List of paper dictionaries (raw or filtered)
        """
        venue_id = self.get_venue_id(conference, year)
        if not venue_id:
            return []
        
        # If we have a search query, fetch more papers and filter
        # This is more efficient than fetching ALL papers
        if search_query and not fetch_all:
            fetch_limit = min(limit * 5, 500)  # Fetch 5x limit or max 500
            papers = self.get_venue_submissions(venue_id, limit=fetch_limit, offset=0)
            # Filter papers
            filtered = self._filter_papers(papers, search_query)
            return filtered[:limit]
        
        if not fetch_all:
            # Simple case: just fetch the requested number
            return self.get_venue_submissions(venue_id, limit=limit, offset=0)
        
        # Fetch all papers with pagination
        logger.info(f"Starting to fetch ALL papers from {venue_id} with pagination...")
        all_papers = []
        offset = 0
        batch_size = 1000  # OpenReview max per request
        batch_num = 1
        
        while True:
            logger.info(f"Fetching batch {batch_num} (offset: {offset}, batch_size: {batch_size})...")
            papers = self.get_venue_submissions(venue_id, limit=batch_size, offset=offset)
            if not papers:
                logger.info(f"No more papers found. Pagination complete.")
                break
            
            all_papers.extend(papers)
            logger.info(f"✓ Batch {batch_num} complete: fetched {len(papers)} papers. Total so far: {len(all_papers)}")
            
            if len(papers) < batch_size:
                # Reached the end
                logger.info(f"Last batch was smaller ({len(papers)} < {batch_size}). Reached end of conference.")
                break
            
            offset += batch_size
            batch_num += 1
        
        logger.info(f"✓ COMPLETED: Fetched total of {len(all_papers)} papers from {venue_id}")
        return all_papers
    
    def get_paper_details(self, paper_id: str) -> Optional[Dict]:
        """
        Fetch detailed information for a specific paper
        
        Args:
            paper_id: OpenReview paper ID
            
        Returns:
            Paper details dictionary
        """
        logger.info(f"Fetching details for paper: {paper_id}")
        url = f"{self.base_url}/notes"
        params = {'id': paper_id}
        
        try:
            self._rate_limit()
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            notes = data.get('notes', [])
            if notes:
                logger.info(f"Successfully fetched details for paper: {paper_id}")
                return notes[0]
            else:
                logger.warning(f"No details found for paper: {paper_id}")
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error(f"Rate limit exceeded for paper {paper_id}: {e}")
            else:
                logger.error(f"HTTP error fetching paper {paper_id}: {e}")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for paper {paper_id}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching paper {paper_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON for paper {paper_id}: {e}")
            return None
    
    def normalize_author_name(self, name: str) -> str:
        """
        Normalize author names for consistency
        
        Args:
            name: Author name in any format
            
        Returns:
            Normalized author name
        """
        if not name or not isinstance(name, str):
            return ""
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Strip common suffixes (Jr., Sr., PhD, etc.)
        suffixes = [' Jr.', ' Sr.', ' Jr', ' Sr', ' II', ' III', ' PhD', ' Ph.D.']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()
        
        return name.strip()
    
    def _filter_papers(self, papers: List[Dict], search_query: str) -> List[Dict]:
        """
        Filter papers by search query (case-insensitive search in title, abstract, authors)
        
        Args:
            papers: List of raw paper dictionaries
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
                content = paper.get('content', {})
                
                # Search in title
                title = content.get('title', {}).get('value', '') if isinstance(content.get('title'), dict) else content.get('title', '')
                if search_lower in title.lower():
                    filtered.append(paper)
                    continue
                
                # Search in abstract
                abstract = content.get('abstract', {}).get('value', '') if isinstance(content.get('abstract'), dict) else content.get('abstract', '')
                if search_lower in abstract.lower():
                    filtered.append(paper)
                    continue
                
                # Search in authors
                authors = content.get('authors', {}).get('value', []) if isinstance(content.get('authors'), dict) else content.get('authors', [])
                if any(search_lower in author.lower() for author in authors):
                    filtered.append(paper)
                    continue
                    
            except (AttributeError, TypeError):
                continue
        
        logger.info(f"Filtered {len(filtered)} papers from {len(papers)} using query '{search_query}'")
        return filtered
    
    def extract_paper_info(self, paper: Dict, conference: str = None) -> Dict:
        """
        Extract relevant information from paper data with normalization
        
        Args:
            paper: Raw paper data from OpenReview
            conference: Conference name (optional, for metadata)
            
        Returns:
            Cleaned paper information dictionary
        """
        try:
            content = paper.get('content', {})
            paper_id = paper.get('id')
            
            # Extract and normalize authors
            raw_authors = content.get('authors', {}).get('value', [])
            normalized_authors = [self.normalize_author_name(author) for author in raw_authors]
            
            # Extract keywords and ensure they're a list
            keywords = content.get('keywords', {}).get('value', [])
            if not isinstance(keywords, list):
                keywords = []
            
            info = {
                'id': paper_id,
                'conference': conference,
                'title': content.get('title', {}).get('value', 'N/A'),
                'abstract': content.get('abstract', {}).get('value', 'N/A'),
                'authors': normalized_authors,
                'raw_authors': raw_authors,
                'keywords': keywords,
                'tldr': content.get('TL;DR', {}).get('value', 'N/A'),
                'pdf_url': f"https://openreview.net/pdf?id={paper_id}" if paper_id else None,
                'forum_url': f"https://openreview.net/forum?id={paper_id}" if paper_id else None,
                'created_time': datetime.fromtimestamp(paper.get('cdate', 0) / 1000).isoformat(),
                'modified_time': datetime.fromtimestamp(paper.get('mdate', 0) / 1000).isoformat(),
            }
            
            logger.debug(f"Extracted info for paper: {paper_id}")
            return info
            
        except Exception as e:
            logger.error(f"Error extracting paper info: {e}")
            logger.error(f"Paper data: {paper.get('id', 'unknown')}")
            return {
                'id': paper.get('id'),
                'conference': conference,
                'title': 'Error extracting title',
                'abstract': 'Error extracting abstract',
                'authors': [],
                'raw_authors': [],
                'keywords': [],
                'tldr': 'N/A',
                'pdf_url': None,
                'forum_url': None,
                'created_time': datetime.now().isoformat(),
                'modified_time': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def download_pdf(self, paper_id: str, output_path: str) -> bool:
        """
        Download PDF for a specific paper
        
        Args:
            paper_id: OpenReview paper ID
            output_path: Local path to save PDF
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Downloading PDF for paper {paper_id} to {output_path}")
        pdf_url = f"https://openreview.net/pdf?id={paper_id}"
        
        try:
            self._rate_limit()
            response = self.session.get(pdf_url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = 0
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    total_size += len(chunk)
            
            logger.info(f"PDF downloaded successfully: {output_path} ({total_size} bytes)")
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error(f"Rate limit exceeded downloading PDF for {paper_id}")
            else:
                logger.error(f"HTTP error downloading PDF for {paper_id}: {e}")
            return False
        except requests.exceptions.Timeout:
            logger.error(f"Timeout downloading PDF for {paper_id}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading PDF for {paper_id}: {e}")
            return False
        except IOError as e:
            logger.error(f"Error writing PDF file {output_path}: {e}")
            return False


def main():
    """Demo usage showing both NeurIPS and ICML"""
    scraper = ConferenceScraper()
    
    # Test both conferences
    for conference in ['neurips', 'icml']:
        print(f"\n{'='*80}")
        print(f"Testing {conference.upper()} scraper")
        print(f"{'='*80}\n")
        
        papers = scraper.get_conference_papers(conference, 2024, limit=5)
        
        if papers:
            print(f"Found {len(papers)} papers from {conference.upper()} 2024\n")
            
            for i, paper in enumerate(papers, 1):
                info = scraper.extract_paper_info(paper, conference=conference.upper())
                
                print(f"Paper {i}:")
                print(f"  Title: {info['title']}")
                print(f"  Authors: {', '.join(info['authors'][:3])}{'...' if len(info['authors']) > 3 else ''}")
                print(f"  Keywords: {', '.join(info['keywords'][:5])}")
                print(f"  PDF: {info['pdf_url']}")
                print()
            
            # Save sample
            first_paper_info = scraper.extract_paper_info(papers[0], conference=conference.upper())
            output_file = f"sample_{conference}_paper.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(first_paper_info, f, indent=2, ensure_ascii=False)
            print(f"Sample saved to {output_file}\n")
        else:
            print(f"No papers found for {conference.upper()} 2024\n")


if __name__ == "__main__":
    main()

