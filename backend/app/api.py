from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timezone
from .scraper.static_scraper import scrape_static
from .scraper.js_scraper import scrape_with_playwright
from .scraper.section_parser import parse_sections
from fastapi.responses import JSONResponse

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: HttpUrl

#Route for GET /healthz
@router.get("/healthz")
def healthz():
    return {"status": "ok"}


#Route for POST /scrape
@router.post("/scrape")
async def scrape(req: ScrapeRequest):
    url = str(req.url)
    result = {
      "url": url,
      "scrapedAt": datetime.now(timezone.utc).isoformat(),
      "meta": {},
      "sections": [],
      "interactions": {"clicks": [], "scrolls": 0, "pages": [url]},
      "errors": []
    }

    # 1) Try static fetch
    try:
        html, meta = await scrape_static(url)
        result["meta"].update(meta)
        sections = parse_sections(html, base_url=url)
    except Exception as e:
        result["errors"].append({"message": f"Static fetch error: {e}", "phase": "fetch"})
        sections = []

    # 2) Heuristic: If need JS fallback
    def needs_js(sections, meta):
        text_len = sum(len(s.get("content", {}).get("text","")) for s in sections)
        if text_len < 200 or not sections:
            return True
        return False

    if needs_js(sections, result["meta"]):
        try:
            js_html, js_meta, interactions = await scrape_with_playwright(url)
            result["meta"].update({k:v for k,v in js_meta.items() if v})
            sections = parse_sections(js_html, base_url=url)
            result["interactions"].update(interactions)
        except Exception as e:
            result["errors"].append({"message": f"Playwright error: {e}", "phase": "render"})

    result["sections"] = sections
    return JSONResponse({"result": result})
