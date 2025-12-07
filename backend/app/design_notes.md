# Design Notes

## Static vs JS Fallback
- Strategy: Attempt static fetch first (httpx + BeautifulSoup). If static content is insufficient (word count < 200, no sections, or no headings), fallback to Playwright for JS rendering.
- Rationale: Most pages are static; Playwright is heavier and slower so we only use it when necessary.

## Wait Strategy for JS
- [x] Network idle (primary)
- [x] Fixed sleep (short: 500-1500ms after clicks)
- [x] Wait for selectors (if we find important selectors)
Details: We attempt `page.goto(..., wait_until="networkidle")`. After clicks/scrolls we use short waits (500–1500ms) and small incremental increases when scrolling.

## Click & Scroll Strategy
- Click flows implemented: role=tab, button[aria-controls], and buttons with text "Load more"/"Show more".
- Scroll/pagination: scroll down up to 3 times (increasing wait). Follow next page links (rel=next or a[href*="page="]) up to depth 3.
- Stop conditions: max_scrolls=3, max_pages=3, per-action timeout 5–30s.

## Section Grouping & Labels
- Group by landmarks (`main`, `section`, `article`, `header`, `nav`, `footer`) first. Fallback group by headings (h1–h3) and following nodes.
- Derive `type`: basic mapping (header->nav, footer->footer, main->section). If no match, use 'unknown'.
- Derive `label`: first heading in section or first 5–7 words of section text.

## Noise Filtering & Truncation
- Filter selectors: '.cookie', '#cookie-consent', '.modal', '.newsletter-popup'.
- `rawHtml` truncated to 2000–4000 characters. `truncated` true when truncated.
