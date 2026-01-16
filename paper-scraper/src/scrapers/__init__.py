"""
Paper scraper package for academic conferences.
Supports OpenReview-based conferences (NeurIPS, ICML, ICLR) and ACL Anthology.
"""

from .openreview_scraper import ConferenceScraper
from .acl_scraper import ACLScraper

__all__ = ['ConferenceScraper', 'ACLScraper']
__version__ = '0.1.0'
