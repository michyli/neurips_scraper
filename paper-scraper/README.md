# Paper Scraper

Academic paper scraper and explorer for AI/ML/NLP conferences.

## Overview

This project scrapes papers from major academic conferences and provides a searchable database with citation networks, author profiles, and visualizations.

## Supported Conferences

### OpenReview-based (via OpenReview API)

- **NeurIPS** - Neural Information Processing Systems
- **ICML** - International Conference on Machine Learning
- **ICLR** - International Conference on Learning Representations

### ACL Anthology (via web scraping)

- **ACL** - Association for Computational Linguistics
- **EMNLP** - Empirical Methods in Natural Language Processing
- **NAACL** - North American Chapter of the ACL
- **EACL** - European Chapter of the ACL
- **COLING** - International Conference on Computational Linguistics

## Project Structure

```
paper-scraper/
├── src/
│   ├── scrapers/          # Conference scrapers
│   │   ├── openreview_scraper.py  # NeurIPS, ICML, ICLR
│   │   ├── acl_scraper.py         # ACL, EMNLP, etc.
│   │   └── neurips_scraper.py     # Original NeurIPS-only scraper
│   ├── database/          # Database models and migrations (TODO)
│   ├── api/               # REST API endpoints (TODO)
│   └── frontend/          # Web interface (TODO)
├── tests/                 # Unit and integration tests
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### OpenReview Conferences (NeurIPS, ICML, ICLR)

```python
from scrapers import ConferenceScraper

scraper = ConferenceScraper()

# Fetch papers from NeurIPS 2024
papers = scraper.get_conference_papers('neurips', 2024, limit=100)

# Extract paper information
for paper in papers:
    info = scraper.extract_paper_info(paper, conference='NeurIPS')
    print(f"{info['title']} by {', '.join(info['authors'][:3])}")
```

### ACL Anthology (ACL, EMNLP, etc.)

```python
from scrapers import ACLScraper

scraper = ACLScraper()

# Fetch papers from ACL 2024
papers = scraper.get_conference_papers('acl', 2024, limit=100)

for paper in papers:
    print(f"{paper['title']} ({paper['year']})")
    print(f"Authors: {', '.join(paper['authors'][:3])}")
    print(f"PDF: {paper['pdf_url']}")
```

## Features

### Current ✅

- Scraping from OpenReview and ACL Anthology
- Robust error handling with automatic retries
- Rate limiting to prevent API throttling
- Data normalization (author names, keywords)
- Comprehensive logging
- 17 unit tests (all passing)

### Planned 🚧

- PostgreSQL database for storing papers
- Full-text search with Elasticsearch/PostgreSQL FTS
- Citation network extraction and matching
- Author disambiguation and profiles
- REST API for programmatic access
- Web interface for browsing and visualization
- Citation graph visualizations
- Publication trend analytics

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_normalization.py
```

### Adding a New Conference

#### OpenReview Conference

Edit `CONFERENCE_VENUES` in `src/scrapers/openreview_scraper.py`:

```python
CONFERENCE_VENUES = {
    'colm': {
        'name': 'COLM',
        'venue_template': 'COLM.cc/{year}/Conference',
        'years': [2024, 2023]
    }
}
```

#### ACL Anthology Venue

Edit `ACL_VENUES` in `src/scrapers/acl_scraper.py`:

```python
ACL_VENUES = {
    'conll': {
        'name': 'CoNLL',
        'full_name': 'Conference on Natural Language Learning',
        'volumes': ['main']
    }
}
```

## Documentation

- [Architecture Overview](docs/SCRAPER_ARCHITECTURE.md)
- [Implementation Details](docs/IMPROVEMENTS.md)
- [Project Timeline](docs/PROJECT_TIMELINE.md)

## Performance

- **OpenReview**: ~100-120 papers/minute
- **ACL Anthology**: ~80-100 papers/minute
- **Memory**: ~50-100MB per 1000 papers

## License

MIT

## Contributing

This is currently a research project by Hojicha Research. For questions or contributions, please reach out to the team.

