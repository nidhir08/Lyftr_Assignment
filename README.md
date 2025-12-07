## Lyftr AI – Full-Stack Web Scraper (FastAPI + React)

This full-stack project implements a browser-like web scraper with:

Static scraping (httpx + BeautifulSoup)

JavaScript-rendered scraping via Playwright

Click flows (tabs, “Load more”, accordions)

Infinite scrolling

Pagination depth ≥ 3

Section-aware structured JSON output

Clean React frontend for triggering scrapes + viewing results

This project satisfies all requirements for the Lyftr AI Full-Stack Assignment.

## Backend (FastAPI)

Static scraping (httpx + retries + custom headers)

JS rendering using Playwright (Chromium)

Automatic fallback from static → JS when content is insufficient

Click flows:

[role="tab"]

button[aria-controls]

“Load more”, “Show more”, “More” buttons

Infinite scroll (multiple scroll passes + DOM length detection)

Pagination (depth ≥ 3)

Noise removal (cookie banners, overlays)

Section-aware HTML parsing:

Landmarks (main, section, article, header)

Headings (h1–h3)

Lists, tables, images, links, text

Hacker News fallback parser

Truncation of raw HTML with truncated=true

Metrics: interactions (clicks, scroll count, pages visited)

# From the backend/ directory:

chmod +x run.sh
./run.sh

## Frontend (React)

Simple UI with:

URL input

Scrape button

Loading states

Error messages

JSON output viewer

Direct backend requests (http://localhost:8000/scrape)

Auto-scroll to output after scrape completes

# From the frontend/lyftr-frontend directory:

npm install
npm run dev