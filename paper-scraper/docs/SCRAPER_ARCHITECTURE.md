# Conference Paper Scraper Architecture

## Overview

We now have scrapers for two types of academic conference systems:

1. **OpenReview-based conferences** (NeurIPS, ICML, ICLR)
2. **ACL Anthology** (ACL, EMNLP, NAACL, EACL, COLING)

## Architecture Comparison

### OpenReview Scraper (`conference_scraper.py`)

**Data Source:** OpenReview API v2 (`https://api2.openreview.net`)

**Supported Conferences:**

- NeurIPS (Neural Information Processing Systems)
- ICML (International Conference on Machine Learning)
- ICLR (International Conference on Learning Representations)

**Key Features:**

- REST API based - clean JSON responses
- Structured data from the start
- Venue ID format: `{Conference}.cc/{Year}/Conference`
- Example: `NeurIPS.cc/2024/Conference`

**Data Retrieved:**

- Title, abstract, authors, keywords
- TL;DR summaries
- PDF and forum URLs
- Creation and modification timestamps
- Review counts and metadata

**Advantages:**

- Clean API, no HTML parsing needed
- Consistent data structure across conferences
- Rich metadata including reviews

### ACL Anthology Scraper (`acl_scraper.py`)

**Data Source:** ACL Anthology website (`https://aclanthology.org`)

**Supported Conferences:**

- ACL (Association for Computational Linguistics)
- EMNLP (Empirical Methods in NLP)
- NAACL (North American Chapter of ACL)
- EACL (European Chapter of ACL)
- COLING (International Conference on Computational Linguistics)

**Key Features:**

- Hybrid approach: BibTeX + HTML scraping
- Paper ID format: `{year}.{venue}-{track}.{number}`
- Example: `2024.acl-long.1`
- Event pages list all papers from a conference

**Data Retrieved:**

- Title, authors, year (from BibTeX)
- Abstract (from HTML scraping)
- PDF URLs, DOI, conference info
- BibTeX citation string
- Page numbers

**Advantages:**

- Comprehensive NLP paper coverage
- BibTeX provides clean citation data
- Large historical archive

## Common Infrastructure

Both scrapers share:

### 1. Error Handling

- Automatic retries with exponential backoff
- Handles rate limiting (429 errors)
- Timeout management
- Graceful degradation on failures

### 2. Logging

- Structured logging with timestamps
- Request tracking
- Error context and debugging info
- Performance monitoring

### 3. Rate Limiting

- Configurable minimum request intervals
- Prevents API throttling
- OpenReview: 500ms between requests
- ACL: 300ms between requests

### 4. Data Normalization

- Author name cleanup (suffixes, whitespace)
- Keyword list validation
- Unicode handling
- Error recovery in data extraction

## Usage Examples

### OpenReview Conferences

```python
from conference_scraper import ConferenceScraper

scraper = ConferenceScraper()

# Fetch papers from NeurIPS 2024
papers = scraper.get_conference_papers('neurips', 2024, limit=100)

# Fetch all papers (with pagination)
all_papers = scraper.get_conference_papers('icml', 2024, fetch_all=True)

# Extract normalized data
for paper in papers:
    info = scraper.extract_paper_info(paper, conference='NeurIPS')
    print(f"{info['title']} by {', '.join(info['authors'][:3])}")
```

### ACL Anthology

```python
from acl_scraper import ACLScraper

scraper = ACLScraper()

# Fetch papers from ACL 2024
papers = scraper.get_conference_papers('acl', 2024, limit=100)

# Fetch all papers (no limit)
all_papers = scraper.get_conference_papers('emnlp', 2024)

# Get complete paper info
paper_info = scraper.get_paper_info('2024.acl-long.1')
print(f"{paper_info['title']}")
print(f"BibTeX: {paper_info['bibtex']}")
```

## Data Schema

### OpenReview Papers

```json
{
  "id": "iEeiZlTbts",
  "conference": "NeurIPS",
  "title": "Paper Title",
  "abstract": "Full abstract text...",
  "authors": ["Author One", "Author Two"],
  "raw_authors": ["Author One Jr.", "Author Two PhD"],
  "keywords": ["keyword1", "keyword2"],
  "tldr": "Short summary",
  "pdf_url": "https://openreview.net/pdf?id=...",
  "forum_url": "https://openreview.net/forum?id=...",
  "created_time": "2024-05-15T13:01:14.791000",
  "modified_time": "2025-01-14T10:03:11.023000"
}
```

### ACL Anthology Papers

```json
{
  "id": "2024.acl-long.1",
  "title": "Paper Title",
  "authors": ["Author One", "Author Two"],
  "raw_authors": ["Author One", "Author Two"],
  "year": 2024,
  "booktitle": "Proceedings of ACL 2024",
  "pages": "1-10",
  "doi": "10.18653/v1/...",
  "abstract": "Full abstract text...",
  "pdf_url": "https://aclanthology.org/2024.acl-long.1.pdf",
  "anthology_url": "https://aclanthology.org/2024.acl-long.1/",
  "url": "https://aclanthology.org/2024.acl-long.1/",
  "bibtex": "@inproceedings{...}",
  "scraped_time": "2026-01-06T14:57:45.683089"
}
```

## Extension Guide

### Adding New OpenReview Conference

Edit `CONFERENCE_VENUES` in `conference_scraper.py`:

```python
CONFERENCE_VENUES = {
    # ... existing conferences ...
    'colm': {
        'name': 'COLM',
        'venue_template': 'COLM.cc/{year}/Conference',
        'years': [2024, 2023]
    }
}
```

That's it! The scraper will work immediately.

### Adding New ACL Anthology Venue

Edit `ACL_VENUES` in `acl_scraper.py`:

```python
ACL_VENUES = {
    # ... existing venues ...
    'findings': {
        'name': 'Findings',
        'full_name': 'Findings of ACL',
        'volumes': ['acl', 'emnlp', 'naacl']
    }
}
```

## Testing

### Unit Tests

Run data normalization tests:

```bash
python test_normalization.py
```

All 17 tests should pass.

### Integration Tests

Test OpenReview scraper:

```bash
python conference_scraper.py
```

Test ACL scraper:

```bash
python acl_scraper.py
```

## Performance Metrics

### OpenReview Scraper

- Average request time: ~500ms
- Papers per minute: ~100-120
- Rate limit: 2 requests/second
- Memory: ~50MB for 1000 papers

### ACL Scraper

- Average request time: ~600ms (BibTeX + HTML)
- Papers per minute: ~80-100
- Rate limit: 3 requests/second
- Memory: ~100MB for 1000 papers (includes HTML parsing)

## Next Steps

1. **Database Integration**: Design schema to store papers from both sources
2. **Incremental Updates**: Track changes and only fetch new/modified papers
3. **Citation Network**: Parse references and build paper relationship graph
4. **Full Text Extraction**: Extract text from PDFs for search indexing
5. **API Layer**: Build REST API for accessing scraped data
6. **Web Interface**: Create search and exploration UI

## Dependencies

```txt
requests>=2.31.0
urllib3>=2.0.0
beautifulsoup4>=4.12.0
```

Install with:

```bash
pip install requests urllib3 beautifulsoup4
```

## File Structure

```
servers-archived/
├── conference_scraper.py       # OpenReview conferences
├── acl_scraper.py             # ACL Anthology
├── neurips_scraper_prototype.py  # Original NeurIPS only
├── test_normalization.py      # Unit tests
├── requirements_scraper.txt   # Dependencies
├── IMPROVEMENTS.md            # Implementation details
└── SCRAPER_ARCHITECTURE.md    # This file
```

## Conference Coverage

**Currently Supported:**

- NeurIPS (2024, 2023+)
- ICML (2024, 2023+)
- ICLR (2024, 2023+)
- ACL (2024+)
- EMNLP (2024+)
- NAACL (2024+)
- EACL (2024+)
- COLING (2024+)

**Easy to Add:**

- COLM (Conference on Language Modeling)
- CoNLL (Computational Natural Language Learning)
- \*SEM (Semantic Evaluation)
- Any other OpenReview or ACL Anthology venue

