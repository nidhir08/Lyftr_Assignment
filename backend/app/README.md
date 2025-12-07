# Lyftr Scraper — Backend
FastAPI backend for the Lyftr AI full-stack assignment.  
Implements static scraping (httpx + BeautifulSoup), Playwright JS rendering fallback, click flows, infinite scroll / pagination, and returns section-aware JSON.

## What’s included 
- `run.sh` — create venv, install deps, install Playwright browsers, start server.
- `requirements.txt` — Python dependencies.
- `app/`
  - `main.py` — FastAPI app + optional static file mounting.
  - `api.py` — `/healthz` and `/scrape` endpoints.
  - `scraper/`
    - `static_scraper.py` — httpx + BeautifulSoup static fetch + metadata extraction.
    - `js_scraper.py` — Playwright rendering, click flows, scroll, pagination.
    - `section_parser.py` — transforms HTML -> section-aware JSON.
  - `design_notes.md` — design decisions, heuristics, wait strategy.
  - `capabilities.json` — booleans describing implemented features.


## Requirements
- Python 3.10+
- Playwright (browsers must be installed; `python -m playwright install`).


## Quick start 
Run from the `backend/` folder:
uvicorn app.main:app --host 0.0.0.0 --port 8000
```bash
chmod +x run.sh     
./run.sh

## Tested Websites & Supported Behaviors

This scraper was validated across multiple website types, verifying:

**1. Single Static Page Rendering**

URL: https://en.wikipedia.org/wiki/Artificial_intelligence

**Checks:**

Static HTML fetched successfully

Metadata extracted

Section parser correctly identifies headings & content

JS fallback triggered only if needed

**2. JavaScript-Rendered Pages**

URLs: https://nextjs.org/

**Checks:**

Playwright loads full DOM

Tabs, components, or accordions that require JS become visible

Click events detected (interactions.clicks)

Scroll triggers additional content loading

Section parser extracts new HTML areas

**3. Pages Requiring Load-More Button Clicks**

URLs: https://dev.to/t/javascript

**Checks:**

Click flows detect & click Load More / Show More buttons

New items appear → DOM growth detected

interactions.clicks.append("load-more clicked")

Infinite scroll + click combination both work

**4. Pagination Depth ≥ 3 (Multi-Page Crawling)**

URL: https://news.ycombinator.com/

**Pagination behavior:**

Follows More → ?p=2 → ?p=3

Records visited pages under interactions.pages

Extracts sections across all pages

Ensures navigation loop avoids revisiting links