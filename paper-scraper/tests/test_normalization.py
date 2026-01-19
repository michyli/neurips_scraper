#!/usr/bin/env python3
"""
Unit tests for data normalization in NeurIPS scraper
"""

import unittest
from neurips_scraper_prototype import NeurIPSScraper


class TestAuthorNormalization(unittest.TestCase):
    """Test cases for author name normalization"""
    
    def setUp(self):
        self.scraper = NeurIPSScraper()
    
    def test_normalize_basic_name(self):
        """Test basic name normalization"""
        self.assertEqual(
            self.scraper.normalize_author_name("John Smith"),
            "John Smith"
        )
    
    def test_normalize_extra_whitespace(self):
        """Test removal of extra whitespace"""
        self.assertEqual(
            self.scraper.normalize_author_name("John   Smith"),
            "John Smith"
        )
        self.assertEqual(
            self.scraper.normalize_author_name("  John Smith  "),
            "John Smith"
        )
    
    def test_normalize_suffix_jr(self):
        """Test removal of Jr. suffix"""
        self.assertEqual(
            self.scraper.normalize_author_name("John Smith Jr."),
            "John Smith"
        )
        self.assertEqual(
            self.scraper.normalize_author_name("John Smith Jr"),
            "John Smith"
        )
    
    def test_normalize_suffix_sr(self):
        """Test removal of Sr. suffix"""
        self.assertEqual(
            self.scraper.normalize_author_name("John Smith Sr."),
            "John Smith"
        )
    
    def test_normalize_suffix_roman_numerals(self):
        """Test removal of Roman numeral suffixes"""
        self.assertEqual(
            self.scraper.normalize_author_name("John Smith II"),
            "John Smith"
        )
        self.assertEqual(
            self.scraper.normalize_author_name("John Smith III"),
            "John Smith"
        )
    
    def test_normalize_suffix_phd(self):
        """Test removal of PhD suffix"""
        self.assertEqual(
            self.scraper.normalize_author_name("John Smith PhD"),
            "John Smith"
        )
        self.assertEqual(
            self.scraper.normalize_author_name("John Smith Ph.D."),
            "John Smith"
        )
    
    def test_normalize_empty_string(self):
        """Test handling of empty string"""
        self.assertEqual(
            self.scraper.normalize_author_name(""),
            ""
        )
    
    def test_normalize_none(self):
        """Test handling of None"""
        self.assertEqual(
            self.scraper.normalize_author_name(None),
            ""
        )
    
    def test_normalize_unicode_names(self):
        """Test handling of Unicode characters in names"""
        self.assertEqual(
            self.scraper.normalize_author_name("José García"),
            "José García"
        )
        self.assertEqual(
            self.scraper.normalize_author_name("北京  Zhang"),
            "北京 Zhang"
        )
    
    def test_normalize_hyphenated_names(self):
        """Test handling of hyphenated names"""
        self.assertEqual(
            self.scraper.normalize_author_name("Mary-Jane Watson"),
            "Mary-Jane Watson"
        )


class TestPaperInfoExtraction(unittest.TestCase):
    """Test cases for paper info extraction"""
    
    def setUp(self):
        self.scraper = NeurIPSScraper()
    
    def test_extract_basic_paper(self):
        """Test extraction of basic paper info"""
        paper_data = {
            'id': 'test123',
            'content': {
                'title': {'value': 'Test Paper'},
                'abstract': {'value': 'Test abstract'},
                'authors': {'value': ['John Smith', 'Jane Doe']},
                'keywords': {'value': ['ML', 'AI']},
                'TL;DR': {'value': 'Test TLDR'}
            },
            'cdate': 1609459200000,  # 2021-01-01
            'mdate': 1609459200000
        }
        
        info = self.scraper.extract_paper_info(paper_data)
        
        self.assertEqual(info['id'], 'test123')
        self.assertEqual(info['title'], 'Test Paper')
        self.assertEqual(info['abstract'], 'Test abstract')
        self.assertEqual(len(info['authors']), 2)
        self.assertEqual(info['authors'][0], 'John Smith')
        self.assertEqual(len(info['keywords']), 2)
    
    def test_extract_paper_with_author_normalization(self):
        """Test that author names are normalized during extraction"""
        paper_data = {
            'id': 'test456',
            'content': {
                'title': {'value': 'Test Paper'},
                'abstract': {'value': 'Test'},
                'authors': {'value': ['John Smith Jr.', 'Jane  Doe  PhD']},
                'keywords': {'value': []},
                'TL;DR': {'value': ''}
            },
            'cdate': 1609459200000,
            'mdate': 1609459200000
        }
        
        info = self.scraper.extract_paper_info(paper_data)
        
        self.assertEqual(info['authors'][0], 'John Smith')
        self.assertEqual(info['authors'][1], 'Jane Doe')
        # Check raw authors are preserved
        self.assertEqual(info['raw_authors'][0], 'John Smith Jr.')
        self.assertEqual(info['raw_authors'][1], 'Jane  Doe  PhD')
    
    def test_extract_paper_missing_fields(self):
        """Test extraction with missing fields"""
        paper_data = {
            'id': 'test789',
            'content': {},
            'cdate': 1609459200000,
            'mdate': 1609459200000
        }
        
        info = self.scraper.extract_paper_info(paper_data)
        
        self.assertEqual(info['id'], 'test789')
        self.assertEqual(info['title'], 'N/A')
        self.assertEqual(info['authors'], [])
        self.assertEqual(info['keywords'], [])
    
    def test_extract_paper_invalid_keywords(self):
        """Test extraction when keywords is not a list"""
        paper_data = {
            'id': 'test999',
            'content': {
                'title': {'value': 'Test'},
                'abstract': {'value': 'Test'},
                'authors': {'value': []},
                'keywords': {'value': 'not-a-list'},  # Invalid
                'TL;DR': {'value': ''}
            },
            'cdate': 1609459200000,
            'mdate': 1609459200000
        }
        
        info = self.scraper.extract_paper_info(paper_data)
        
        # Should default to empty list
        self.assertEqual(info['keywords'], [])
    
    def test_extract_paper_with_exception(self):
        """Test extraction handles exceptions gracefully"""
        paper_data = {
            'id': 'test_error',
            'content': None  # Will cause error
        }
        
        info = self.scraper.extract_paper_info(paper_data)
        
        # Should return error info instead of crashing
        self.assertEqual(info['id'], 'test_error')
        self.assertIn('error', info)
        self.assertEqual(info['authors'], [])


class TestURLGeneration(unittest.TestCase):
    """Test cases for URL generation"""
    
    def setUp(self):
        self.scraper = NeurIPSScraper()
    
    def test_pdf_url_generation(self):
        """Test PDF URL generation"""
        paper_data = {
            'id': 'abc123XYZ',
            'content': {
                'title': {'value': 'Test'},
                'abstract': {'value': 'Test'},
                'authors': {'value': []},
                'keywords': {'value': []},
                'TL;DR': {'value': ''}
            },
            'cdate': 1609459200000,
            'mdate': 1609459200000
        }
        
        info = self.scraper.extract_paper_info(paper_data)
        
        self.assertEqual(
            info['pdf_url'],
            'https://openreview.net/pdf?id=abc123XYZ'
        )
        self.assertEqual(
            info['forum_url'],
            'https://openreview.net/forum?id=abc123XYZ'
        )
    
    def test_url_generation_no_id(self):
        """Test URL generation when paper has no ID"""
        paper_data = {
            'content': {
                'title': {'value': 'Test'},
                'abstract': {'value': 'Test'},
                'authors': {'value': []},
                'keywords': {'value': []},
                'TL;DR': {'value': ''}
            },
            'cdate': 1609459200000,
            'mdate': 1609459200000
        }
        
        info = self.scraper.extract_paper_info(paper_data)
        
        self.assertIsNone(info['pdf_url'])
        self.assertIsNone(info['forum_url'])


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)

