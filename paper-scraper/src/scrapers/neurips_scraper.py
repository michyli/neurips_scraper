#!/usr/bin/env python3
"""
NeurIPS Paper Scraper Prototype
Uses OpenReview API to fetch paper metadata from NeurIPS conferences
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


class NeurIPSScraper:
    """Scraper for NeurIPS papers using OpenReview API"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
        self.base_url = "https://api2.openreview.net"
        self.session = requests.Session()
        
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
        
        logger.info(f"Initialized NeurIPSScraper with base_url={self.base_url}")
        
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get_venue_submissions(self, venue_id: str, limit: int = 10) -> List[Dict]:
        """
        Fetch submissions for a given venue (conference)
        
        Args:
            venue_id: OpenReview venue ID (e.g., 'NeurIPS.cc/2024/Conference')
            limit: Maximum number of papers to fetch
            
        Returns:
            List of paper dictionaries
        """
        logger.info(f"Fetching submissions for venue: {venue_id}, limit: {limit}")
        url = f"{self.base_url}/notes"
        params = {
            'invitations': f'{venue_id}/-/Submission',
            'details': 'replyCount,invitation,original',
            'limit': limit
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
    
    def extract_paper_info(self, paper: Dict) -> Dict:
        """
        Extract relevant information from paper data with normalization
        
        Args:
            paper: Raw paper data from OpenReview
            
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
                'title': content.get('title', {}).get('value', 'N/A'),
                'abstract': content.get('abstract', {}).get('value', 'N/A'),
                'authors': normalized_authors,
                'raw_authors': raw_authors,  # Keep original for reference
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
            # Return minimal info rather than failing completely
            return {
                'id': paper.get('id'),
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
    """Demo usage of the scraper"""
    scraper = NeurIPSScraper()
    
    # NeurIPS 2024 venue ID
    venue_id = "NeurIPS.cc/2024/Conference"
    
    print(f"Fetching papers from {venue_id}...")
    papers = scraper.get_venue_submissions(venue_id, limit=5)
    
    if not papers:
        print("No papers found. Trying NeurIPS 2023...")
        venue_id = "NeurIPS.cc/2023/Conference"
        papers = scraper.get_venue_submissions(venue_id, limit=5)
    
    print(f"\nFound {len(papers)} papers\n")
    
    for i, paper in enumerate(papers, 1):
        info = scraper.extract_paper_info(paper)
        
        print(f"Paper {i}:")
        print(f"  Title: {info['title']}")
        print(f"  Authors: {', '.join(info['authors'][:3])}{'...' if len(info['authors']) > 3 else ''}")
        print(f"  Keywords: {', '.join(info['keywords'][:5])}")
        print(f"  TL;DR: {info['tldr'][:100]}..." if len(info['tldr']) > 100 else f"  TL;DR: {info['tldr']}")
        print(f"  PDF: {info['pdf_url']}")
        print(f"  Forum: {info['forum_url']}")
        print()
    
    # Save first paper details to JSON
    if papers:
        first_paper_info = scraper.extract_paper_info(papers[0])
        output_file = "sample_paper.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(first_paper_info, f, indent=2, ensure_ascii=False)
        print(f"Sample paper saved to {output_file}")
        
        # Optional: Download first paper PDF
        # scraper.download_pdf(papers[0]['id'], 'sample_paper.pdf')


if __name__ == "__main__":
    main()

