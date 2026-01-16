# Project Structure

## Directory Layout

```
src/paper-scraper/
│
├── src/                           # Source code
│   ├── __init__.py               # Package initialization
│   └── scrapers/                 # Scraper modules
│       ├── __init__.py           # Exposes ConferenceScraper, ACLScraper
│       ├── openreview_scraper.py # Generic OpenReview scraper (NeurIPS, ICML, ICLR)
│       ├── acl_scraper.py        # ACL Anthology scraper (ACL, EMNLP, etc.)
│       └── neurips_scraper.py    # Original NeurIPS-only prototype
│
├── tests/                         # Test suite
│   ├── test_normalization.py     # Data normalization tests (17 tests)
│   └── test_scraper.py           # Integration tests
│
├── docs/                          # Documentation
│   ├── SCRAPER_ARCHITECTURE.md   # Architecture overview
│   ├── IMPROVEMENTS.md           # Implementation details
│   └── PROJECT_TIMELINE.md       # Development timeline
│
├── pyproject.toml                # Python project configuration
├── requirements.txt              # Dependencies
├── README.md                     # Project overview and usage
├── .gitignore                    # Git ignore rules
└── STRUCTURE.md                  # This file
```

## Module Overview

### `src/scrapers/openreview_scraper.py`

**Class:** `ConferenceScraper`

Handles OpenReview-based conferences through their API v2.

**Supported Conferences:**

- NeurIPS (Neural Information Processing Systems)
- ICML (International Conference on Machine Learning)
- ICLR (International Conference on Learning Representations)

**Key Features:**

- API-based (no HTML scraping)
- Pagination support
- Rate limiting (500ms between requests)
- Automatic retries on failure
- Author name normalization

### `src/scrapers/acl_scraper.py`

**Class:** `ACLScraper`

Handles ACL Anthology conferences through web scraping + BibTeX parsing.

**Supported Conferences:**

- ACL (Association for Computational Linguistics)
- EMNLP (Empirical Methods in Natural Language Processing)
- NAACL (North American Chapter of ACL)
- EACL (European Chapter of ACL)
- COLING (International Conference on Computational Linguistics)

**Key Features:**

- Hybrid approach (BibTeX + HTML)
- Extracts complete citation data
- Rate limiting (300ms between requests)
- Robust error handling

### `src/scrapers/neurips_scraper.py`

**Class:** `NeurIPSScraper`

Original prototype scraper for NeurIPS only. Kept for reference.

**Note:** Use `ConferenceScraper` from `openreview_scraper.py` instead for production code.

## Usage Examples

### Quick Start

```python
# Import scrapers
from scrapers import ConferenceScraper, ACLScraper

# OpenReview conferences
openreview = ConferenceScraper()
papers = openreview.get_conference_papers('neurips', 2024, limit=10)

# ACL Anthology conferences
acl = ACLScraper()
papers = acl.get_conference_papers('acl', 2024, limit=10)
```

### Detailed Example

```python
from scrapers import ConferenceScraper

scraper = ConferenceScraper()

# Fetch papers
papers = scraper.get_conference_papers('neurips', 2024, limit=100)

# Process each paper
for paper in papers:
    info = scraper.extract_paper_info(paper, conference='NeurIPS')

    print(f"Title: {info['title']}")
    print(f"Authors: {', '.join(info['authors'])}")
    print(f"Keywords: {', '.join(info['keywords'])}")
    print(f"PDF: {info['pdf_url']}")
    print(f"Abstract: {info['abstract'][:100]}...")
    print()
```

## Testing

### Run All Tests

```bash
cd src/paper-scraper
python -m pytest tests/ -v
```

### Run Specific Tests

```bash
# Data normalization tests
python tests/test_normalization.py

# Integration tests
python tests/test_scraper.py
```

### Test Coverage

- 17 unit tests for data normalization
- Author name edge cases (suffixes, whitespace, Unicode)
- Paper metadata extraction
- URL generation
- Error handling

## Next Steps

### Phase 1: Database Layer (In Progress)

```
src/
├── database/
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy models
│   ├── schema.sql         # Database schema
│   └── migrations/        # Database migrations
```

### Phase 2: API Layer

```
src/
├── api/
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── routes/
│   │   ├── papers.py      # /papers endpoints
│   │   ├── authors.py     # /authors endpoints
│   │   └── search.py      # /search endpoints
│   └── schemas.py         # Pydantic models
```

### Phase 3: Frontend

```
src/
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── utils/         # Helper functions
│   └── public/            # Static assets
```

## Development Guidelines

### Adding a New Conference

1. **Identify Conference Type**

   - OpenReview-based? → Edit `openreview_scraper.py`
   - ACL Anthology? → Edit `acl_scraper.py`
   - Other? → Create new scraper module

2. **Add Configuration**

   For OpenReview:

   ```python
   CONFERENCE_VENUES = {
       'conference_name': {
           'name': 'Display Name',
           'venue_template': 'Conference.cc/{year}/Conference',
           'years': [2024, 2023, 2022]
       }
   }
   ```

   For ACL:

   ```python
   ACL_VENUES = {
       'venue_name': {
           'name': 'Short Name',
           'full_name': 'Full Conference Name',
           'volumes': ['long', 'short']
       }
   }
   ```

3. **Test the Integration**
   ```bash
   python src/scrapers/openreview_scraper.py
   # or
   python src/scrapers/acl_scraper.py
   ```

### Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to all functions
- Keep functions focused and small
- Log important operations
- Handle errors gracefully

### Commit Guidelines

- Use descriptive commit messages
- Test before committing
- Update documentation when adding features
- Keep commits focused on single changes

## Architecture Decisions

### Why Separate OpenReview and ACL Scrapers?

Different data sources require different approaches:

- **OpenReview**: Clean REST API, structured JSON responses
- **ACL Anthology**: HTML scraping + BibTeX parsing

Keeping them separate:

- Maintains clear separation of concerns
- Makes testing easier
- Allows independent updates
- Each scraper can optimize for its source

### Why Not Use a Single Database Connection?

Currently scrapers are independent for flexibility:

- Can run scrapers without database
- Easier to test scraper logic
- Export to JSON for inspection
- Database layer will be added in Phase 1

### Package Structure Rationale

Following Python best practices:

- `src/` layout prevents import issues
- `tests/` separate from source
- `docs/` for documentation
- `pyproject.toml` for modern Python packaging
- Clear module boundaries

## Dependencies

```
requests>=2.31.0        # HTTP requests
urllib3>=2.0.0          # HTTP client
beautifulsoup4>=4.12.0  # HTML parsing (ACL scraper)
```

## Performance Characteristics

| Metric               | OpenReview | ACL Anthology |
| -------------------- | ---------- | ------------- |
| Papers per minute    | 100-120    | 80-100        |
| Average request time | ~500ms     | ~600ms        |
| Memory per 1K papers | ~50MB      | ~100MB        |
| Rate limit           | 2 req/sec  | 3 req/sec     |

## Known Limitations

1. **NeurIPS 2022 and older** - Different venue ID format, needs investigation
2. **PDF downloads** - No automatic retry on large files
3. **Citation parsing** - Not yet implemented
4. **Author disambiguation** - Basic normalization only
5. **Rate limiting** - Fixed intervals, could be smarter

## Future Enhancements

- [ ] Implement citation network extraction
- [ ] Add author disambiguation with ML
- [ ] Support for COLM, CoNLL conferences
- [ ] Async scraping for better performance
- [ ] Caching layer for repeated requests
- [ ] Admin UI for monitoring scrapers
- [ ] Incremental updates (only fetch new papers)
- [ ] Full-text PDF extraction
- [ ] Semantic search on abstracts

## Support

For questions or issues:

1. Check documentation in `docs/`
2. Review code comments in scrapers
3. Run tests to verify functionality
4. Contact Hojicha Research team

---

Last Updated: 2026-01-10
Version: 0.1.0
