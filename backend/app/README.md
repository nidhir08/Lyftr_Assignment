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
