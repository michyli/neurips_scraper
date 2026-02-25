# Changelog

All notable changes to the Paper Scraper project are documented here.

## [0.2.0] - 2026-01-05

### Added - Frontend Enhancements

**Browse vs Search Modes**
- Toggle between search mode (🔍) and browse mode (📚)
- Browse mode auto-loads papers when conference selected
- Search mode requires explicit search query
- Clear visual distinction between modes

**Expandable Abstracts**
- Long abstracts (>300 chars) collapsed by default
- "Show more ▼" / "Show less ▲" toggle buttons
- Smoother interface, more papers visible at once

**Visual Keyword Tags**
- Keywords displayed as colored pills below paper info
- Up to 6 keywords shown per paper
- Quick topic scanning without reading full abstract

**Statistics Dashboard**
- Stats bar showing paper count, conference, year
- Provides context at a glance
- Updates dynamically with results

**UI/UX Improvements**
- Icons added to mode buttons and paper links
- Better hover effects and animations
- Improved color scheme and contrast
- Professional modern design

### Documentation
- Added `docs/FRONTEND_IMPROVEMENTS.md` with detailed explanation
- Updated `QUICKSTART.md` with new usage instructions
- Backed up original frontend as `index_old.html`

---

## [0.1.1] - 2026-01-05

### Optimized - Backend Performance

**Search Filtering**
- Moved filtering from API layer to scraper level
- Fetch 3-5x limit instead of all papers
- 75% faster searches, 60-80% less memory

**Caching**
- Added in-memory cache with 5-minute TTL
- First query: 5-10 seconds
- Cached queries: <100ms (instant)
- Prevents rate limiting

**Security**
- Added CORS warnings and TODO comments
- Documented production deployment needs

### Documentation
- Added `docs/OPTIMIZATIONS.md` with performance metrics
- Updated `QUICKSTART.md` with performance notes

---

## [0.1.0] - 2026-01-04

### Added - Initial Release

**Scrapers**
- OpenReview scraper for NeurIPS, ICML, ICLR
- ACL Anthology scraper for ACL, EMNLP, NAACL, EACL, COLING
- Robust error handling and retry logic
- Rate limiting (500ms/300ms intervals)
- Author name normalization

**Backend API**
- FastAPI REST API with 3 endpoints
- `/papers/{conference}/{year}` - Get papers
- `/conferences` - List conferences
- `/search` - Search across conferences
- CORS enabled for frontend access

**Frontend**
- Single-page web application
- Conference selection buttons
- Year dropdown selector
- Search functionality
- Responsive design with gradient theme

**Testing**
- 17 unit tests for data normalization
- Integration tests for scrapers
- All tests passing

**Documentation**
- `README.md` - Project overview
- `QUICKSTART.md` - Usage instructions
- `docs/SCRAPER_ARCHITECTURE.md` - Technical details
- `docs/IMPROVEMENTS.md` - Implementation notes
- `docs/PROJECT_TIMELINE.md` - Development roadmap
- `STRUCTURE.md` - Project layout

**Project Structure**
- Proper Python package layout
- `pyproject.toml` for configuration
- `.gitignore` for Python projects
- Clean separation of concerns

---

## Version History

- **0.2.0** - Frontend exploration features
- **0.1.1** - Backend performance optimizations
- **0.1.0** - Initial MVP release

## Future Roadmap

See `docs/PROJECT_TIMELINE.md` for planned features:

- Database layer (PostgreSQL)
- Full-text search (Elasticsearch)
- Citation network extraction
- Author disambiguation
- React frontend with visualizations
- Galaxy view, citation river, author networks
- Paper recommendations
- User accounts and reading lists
- AI-powered summaries

---

**Project:** AI Paper Trails  
**Repository:** https://github.com/michyli/neurips_scraper  
**Team:** Hojicha Research (Michael, Harper, Ray)
