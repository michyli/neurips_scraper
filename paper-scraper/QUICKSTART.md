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

1. **Select a Conference** - Click one of the conference buttons (NeurIPS, ICML, ICLR, ACL, EMNLP, etc.)
2. **Choose a Year** - Select the year from the dropdown (2024, 2023, 2022, 2021)
3. **Optional: Enter Search Query** - Type keywords to filter papers
4. **Click "Search Papers"** - View results below

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

- First search for each conference may take 10-30 seconds as it fetches from the source
- Results are limited to 20 papers by default for faster loading
- Search is case-insensitive and searches title, abstract, and authors
- Papers are fetched live from OpenReview API and ACL Anthology

### Next Steps

- Add database caching for faster repeated searches
- Implement author pages and citation networks
- Add visualization for paper trends
- Deploy to production server
