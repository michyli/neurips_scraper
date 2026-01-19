# Project Timeline Estimate

## AI Conference Paper Scraper & Explorer

Based on Ray's technical challenge assessment, here's a detailed breakdown of work needed to complete the full system.

---

## Current Status ✅

**Completed (Week 1):**

- ✅ NeurIPS scraper prototype
- ✅ Generic OpenReview conference scraper (NeurIPS, ICML, ICLR)
- ✅ ACL Anthology scraper (ACL, EMNLP, NAACL, EACL, COLING)
- ✅ Error handling, logging, rate limiting
- ✅ Data normalization with unit tests (17 tests passing)
- ✅ Basic architecture documentation

---

## Remaining Work

### Phase 1: Database & Storage (3-5 days)

**Tasks:**

1. Design database schema
   - Papers table (id, title, abstract, conference, year, etc.)
   - Authors table with disambiguation fields
   - Conferences table
   - Citations/References junction table
   - Paper-Author junction table (many-to-many)
2. Set up PostgreSQL
   - Install and configure
   - Create tables with proper indexes
   - Add full-text search indexes on title/abstract
3. Object storage for PDFs
   - Choose solution (S3, MinIO, local filesystem)
   - Implement upload/download logic
   - Add deduplication based on paper ID
4. Migration scripts
   - Import existing scraped data
   - Handle schema updates
5. Backup strategy
   - Automated backups
   - Disaster recovery plan

**Complexity Factors:**

- Designing schema to handle papers from multiple sources
- Handling duplicates (same paper in different conferences)
- Efficient indexing for large-scale queries

**Estimated Time: 3-5 days**

---

### Phase 2: Search & Indexing (2-3 days)

**Tasks:**

1. Choose search solution
   - Option A: Elasticsearch (powerful, complex)
   - Option B: PostgreSQL full-text search (simpler, good enough)
   - Option C: Meilisearch (modern, easy to use)
2. Set up search infrastructure
   - Install and configure
   - Define index mappings
3. Implement indexing pipeline
   - Index papers on insert/update
   - Incremental vs full reindex
4. Search features
   - Full-text search on title, abstract, keywords
   - Filters: conference, year, author
   - Sorting: relevance, date, citations
   - Fuzzy matching for typos
5. Performance optimization
   - Query optimization
   - Caching frequent queries

**Complexity Factors:**

- Elasticsearch has learning curve
- Balancing search quality vs performance
- Handling updates without full reindex

**Estimated Time: 2-3 days**
(Could be 1 day if using PostgreSQL FTS instead of Elasticsearch)

---

### Phase 3: Citation Network (5-7 days) 🔴 HIGH COMPLEXITY

**Tasks:**

1. PDF text extraction
   - Use PyMuPDF or pdfplumber
   - Handle different PDF formats
   - Extract references section
2. Reference parsing
   - Identify reference patterns
   - Extract: authors, title, year, venue
   - Handle multiple citation formats (IEEE, ACM, etc.)
   - Use existing parsers (GROBID, Science Parse, or regex)
3. Citation matching
   - Match extracted citations to papers in database
   - Fuzzy matching on title (80%+ similarity)
   - Verify with author names, year
   - Handle partial/incomplete citations
4. Build citation graph
   - Store in database (cited_by, cites relationships)
   - Calculate citation counts
   - Detect citation clusters
5. Testing & validation
   - Manually verify sample of matches
   - Measure precision/recall
   - Handle edge cases

**Complexity Factors:**

- PDFs have inconsistent formatting
- Reference formats vary wildly
- Fuzzy matching is computationally expensive
- Many false positives/negatives
- Abbreviated paper titles in citations
- Author name variations

**Challenges:**

- "Smith et al." - which Smith?
- Preprint vs published versions (different titles)
- Conference papers vs journal versions
- Non-English papers

**Estimated Time: 5-7 days**
(Could extend to 10+ days if accuracy requirements are strict)

**Quick Win Alternative:** Start with just storing raw reference text, implement matching later

---

### Phase 4: Author Disambiguation (3-4 days)

**Tasks:**

1. Author entity resolution
   - Normalize name formats
   - Match "J. Smith", "John Smith", "J.R. Smith"
2. Disambiguation heuristics
   - Same name + same institution → probably same person
   - Same name + co-author overlap → likely same
   - Different institutions + different fields → probably different
3. Build author profiles
   - Aggregate papers by author entity
   - Calculate h-index, citation counts
   - Extract affiliations over time
4. Manual resolution interface (optional)
   - UI for resolving ambiguous cases
   - Export for human review
5. ML approach (advanced, optional)
   - Train classifier on name, co-authors, venues, topics
   - Requires labeled training data

**Complexity Factors:**

- Very common names (e.g., "Wei Wang" in ML)
- Name changes (marriage, transliteration)
- Authors moving institutions
- Incomplete affiliation data

**Estimated Time: 3-4 days (heuristic approach)**
(8-10 days if implementing ML-based system)

---

### Phase 5: REST API (2-3 days)

**Tasks:**

1. Set up FastAPI/Flask
   - Project structure
   - Environment configuration
   - CORS setup
2. Implement endpoints
   - `GET /papers` - search papers
   - `GET /papers/{id}` - paper details
   - `GET /authors/{id}` - author profile
   - `GET /papers/{id}/citations` - citation network
   - `GET /conferences` - list conferences
   - `GET /search/suggest` - autocomplete
3. Authentication & authorization
   - API key generation
   - Rate limiting (per key)
   - Usage tracking
4. Documentation
   - OpenAPI/Swagger spec
   - Example requests
   - Error codes
5. Testing
   - Unit tests for endpoints
   - Integration tests
   - Load testing

**Estimated Time: 2-3 days**

---

### Phase 6: Web Frontend (5-7 days)

**Tasks:**

1. Set up React/Next.js project
   - Project scaffolding
   - UI library (Material-UI, Tailwind)
   - Routing
2. Search interface
   - Search bar with autocomplete
   - Filters (conference, year, author)
   - Results list with pagination
   - Sort options
3. Paper detail page
   - Full metadata display
   - Abstract
   - Authors (clickable to profile)
   - PDF link, BibTeX export
   - Citation graph visualization
4. Author profile page
   - List of papers
   - Co-authors network
   - Publication timeline
   - Citation metrics
5. Visualization components
   - Citation network graph (D3.js, Cytoscape.js)
   - Publication trends over time
   - Conference distribution
6. UI/UX polish
   - Responsive design
   - Loading states
   - Error handling
   - Accessibility

**Complexity Factors:**

- Citation graph visualization is tricky
- Performance with large result sets
- Making it look professional

**Estimated Time: 5-7 days**
(Could be 3-4 days for minimal viable UI)

---

### Phase 7: Incremental Updates & Monitoring (2-3 days)

**Tasks:**

1. Scheduled scrapers
   - Cron jobs or Celery tasks
   - Check for new papers weekly
   - Update existing papers (review scores, citations)
2. Change detection
   - Track last_checked timestamp
   - Only scrape what's new/changed
   - Handle conference additions
3. Monitoring & alerting
   - Scraper health checks
   - Alert when scraper fails
   - Track scraping metrics (papers/day, errors)
   - Database size monitoring
4. Error recovery
   - Retry failed scrapes
   - Log errors for debugging
   - Manual retry interface
5. Admin dashboard
   - View scraper status
   - Trigger manual scrapes
   - See error logs

**Estimated Time: 2-3 days**

---

## Timeline Summary

### Full System (All Features)

| Phase | Component                 | Days | Cumulative |
| ----- | ------------------------- | ---- | ---------- |
| ✅ 0  | Scrapers & Infrastructure | DONE | -          |
| 1     | Database & Storage        | 3-5  | 3-5        |
| 2     | Search & Indexing         | 2-3  | 5-8        |
| 3     | Citation Network          | 5-7  | 10-15      |
| 4     | Author Disambiguation     | 3-4  | 13-19      |
| 5     | REST API                  | 2-3  | 15-22      |
| 6     | Web Frontend              | 5-7  | 20-29      |
| 7     | Monitoring & Updates      | 2-3  | 22-32      |

**Total: 22-32 working days (4-6 weeks)**

### MVP (Minimum Viable Product)

Excluding citation network and advanced author disambiguation:

| Phase | Component               | Days |
| ----- | ----------------------- | ---- |
| 1     | Database & Storage      | 3-5  |
| 2     | Search (PostgreSQL FTS) | 1-2  |
| 4     | Basic Author Matching   | 2    |
| 5     | REST API                | 2-3  |
| 6     | Simple Frontend         | 3-4  |
| 7     | Basic Monitoring        | 1-2  |

**MVP Total: 12-18 working days (2.5-3.5 weeks)**

---

## Risk Factors & Unknowns

### High Risk 🔴

1. **Citation Parsing Accuracy**

   - Unknown: How many edge cases exist in real papers
   - Mitigation: Start with manual validation of 100 samples
   - Could add 5-10 days if accuracy is poor

2. **Scale/Performance Issues**

   - Unknown: Behavior with 100K+ papers
   - Mitigation: Load testing early, optimize queries
   - Could add 3-5 days for optimization

3. **PDF Processing Reliability**
   - Unknown: How many PDFs have issues (corrupted, scanned, etc.)
   - Mitigation: Graceful error handling, manual review queue

### Medium Risk 🟡

1. **Author Disambiguation Quality**

   - Unknown: How good heuristics will be
   - Mitigation: Start simple, iterate based on results

2. **Search Relevance**

   - Unknown: Whether results are useful
   - Mitigation: Get early feedback, tune ranking

3. **API Rate Limiting**
   - Unknown: How heavy usage will be
   - Mitigation: Monitor and adjust

### Low Risk 🟢

1. **Database Design** - well understood problem
2. **REST API** - straightforward implementation
3. **Frontend** - standard web dev work

---

## Recommended Approach

### Option A: Full System (6 weeks)

Build everything Ray suggested. Best for long-term maintainability and feature completeness.

**Pros:**

- Complete solution
- All features available from launch

**Cons:**

- Longest time to first version
- Higher risk of delays

### Option B: MVP then Iterate (3 weeks + ongoing)

Launch MVP without citations, add features incrementally.

**Pros:**

- Faster time to launch
- Can get user feedback early
- Reduced risk

**Cons:**

- Need to plan for adding citations later
- May need database migrations

### Option C: Staged Releases

Week 1-2: Database + Search + API
Week 3: Basic frontend
Week 4-5: Citations
Week 6: Polish + monitoring

**Pros:**

- Regular deliverables
- Can demo progress
- Adjust priorities based on feedback

**Cons:**

- Need careful planning to avoid rework

---

## My Recommendation 💡

**Start with MVP (Option B):**

1. **Weeks 1-2:** Database, Search, API, Basic Frontend
   - Users can search and browse papers
   - Author pages with simple matching
   - Core value proposition proven
2. **Week 3:** Polish MVP, deploy, gather feedback
   - Fix bugs
   - Improve UX based on testing
   - Add missing conferences
3. **Weeks 4-5:** Add citation network
   - Can now iterate based on real usage
   - Prioritize accuracy over coverage
4. **Week 6:** Advanced features
   - Better author disambiguation
   - Visualizations
   - API improvements

This approach:

- Delivers value faster (3 weeks vs 6)
- Reduces risk (citations are hardest part)
- Allows for user feedback before investing in complex features
- Keeps momentum (regular releases)

---

## Next Immediate Steps

1. **Design database schema** (1-2 days)
   - Whiteboard the tables
   - Validate with sample queries
   - Get Ray's feedback
2. **Set up PostgreSQL** (0.5 day)
   - Install, configure
   - Create initial tables
3. **Import scraped data** (0.5 day)
   - Migrate existing JSON to database
   - Verify data integrity
4. **Build basic API** (1 day)
   - Start with /papers endpoint
   - Test with real data

Then reassess based on progress and priorities.

