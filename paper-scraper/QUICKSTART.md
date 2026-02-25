# Quick Start Guide

## Running the Paper Scraper Web App

### 1. Install Dependencies

```bash
cd src/paper-scraper
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
cd src/api
python main.py
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 3. Open the Web Interface

Open `src/frontend/index.html` in your web browser, or serve it with a simple HTTP server:

```bash
cd src/frontend
python -m http.server 3000
```

Then visit `http://localhost:3000`

### 4. Using the Interface

**Two Modes:**

- **🔍 Search Mode** - Find specific papers by keyword
- **📚 Browse Mode** - Explore recent papers without searching

**Search Mode:**

1. **Enter Search Query** - Type keywords for title, author, or topics
2. **Select Conference** - Click one of the conference buttons
3. **Choose Year** - Select from dropdown (2024, 2023, 2022, 2021)
4. **Click "Search Papers"** - View filtered results

**Browse Mode:**

1. **Click "📚 Browse"** toggle at top
2. **Select Conference** - Papers load automatically!
3. **Choose Year** - Select from dropdown
4. **Explore** - Expand abstracts, view keywords, follow links

**Features:**

- ✨ Expandable abstracts (click "Show more")
- 🏷️ Visual keyword tags for quick topic scanning
- 📊 Statistics dashboard showing paper count and filters
- 📄 Direct links to PDFs and conference pages

### Conference Buttons

- **NeurIPS** - Neural Information Processing Systems
- **ICML** - International Conference on Machine Learning
- **ICLR** - International Conference on Learning Representations
- **ACL** - Association for Computational Linguistics
- **EMNLP** - Empirical Methods in Natural Language Processing
- **NAACL** - North American Chapter of the ACL
- **EACL** - European Chapter of the ACL
- **COLING** - International Conference on Computational Linguistics

### Example Searches

- Select **NeurIPS** → Year **2024** → Search **"transformers"**
- Select **ACL** → Year **2024** → Search **"language models"**
- Select **ICML** → Year **2024** → Leave search empty to see recent papers

### API Endpoints

**Get Papers from Conference**

```
GET /papers/{conference}/{year}?limit=20&search=query
```

**List All Conferences**

```
GET /conferences
```

**Search Across Conferences**

```
GET /search?q=query&conference=neurips&year=2024
```

### Troubleshooting

**Error: Connection refused**

- Make sure the API server is running on port 8000
- Check that you started `python main.py` in the `src/api` directory

**Error: No papers found**

- Some conferences may not have data for all years
- Try a different year or conference
- Check API logs for detailed errors

**Error: Module not found**

- Make sure you installed requirements: `pip install -r requirements.txt`
- Ensure you're in the correct directory

### Notes

- **Performance Optimized:** Search filtering happens at the scraper level for faster results
- **Caching Enabled:** Repeated queries are cached for 5 minutes (instant results!)
- First search for a conference/year takes 5-10 seconds; subsequent searches are instant
- Results are limited to 20 papers by default for faster loading
- Search is case-insensitive and searches title, abstract, and authors
- Papers are fetched from OpenReview API and ACL Anthology with efficient filtering

### Performance Optimizations

This MVP includes several optimizations:

- ✅ **Scraper-level filtering** - Search happens before loading all papers
- ✅ **In-memory caching** - 5-minute cache for instant repeated queries
- ✅ **Smart prefetching** - Fetches 3-5x limit to ensure enough search results

See [`docs/OPTIMIZATIONS.md`](docs/OPTIMIZATIONS.md) for detailed technical information.

### Next Steps

- Add PostgreSQL database for persistent storage and full-text search
- Implement Redis for distributed caching
- Add author pages and citation networks
- Add visualization for paper trends
- Deploy to production server with restricted CORS
