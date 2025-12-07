import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import asyncio
import time

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

async def _fetch(url: str, headers: dict, timeout: int = 15, http2: bool = False):
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers, http2=http2, limits=limits) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text

async def scrape_static(url: str, timeout: int = 15):
    try:
        html = await _fetch(url, headers=DEFAULT_HEADERS, timeout=timeout, http2=False)
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        if status == 403:
            alt_headers = DEFAULT_HEADERS.copy()
            alt_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
            time.sleep(0.5)
            try:
                html = await _fetch(url, headers=alt_headers, timeout=timeout, http2=True)
            except Exception:
                raise
        else:
            raise
    except Exception:
        raise

    soup = BeautifulSoup(html, "lxml")
    meta = {}
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = title or og_title["content"]
    meta["title"] = title or ""

    desc = ""
    d = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
    if d and d.get("content"):
        desc = d["content"]
    meta["description"] = desc or ""

    html_tag = soup.find("html")
    meta["language"] = html_tag.get("lang", "") if html_tag else ""

    link = soup.find("link", rel="canonical")
    meta["canonical"] = urljoin(url, link["href"]) if link and link.get("href") else None

    return html, meta
