from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from urllib.parse import urljoin
from urllib.parse import urlparse
import re

def _is_same_origin(a, base):
    try:
        return urlparse(a).netloc == urlparse(base).netloc
    except:
        return False
    

async def _safe_goto(page, url, timeouts=(30000, 10000)):
    try:
        await page.goto(url, wait_until="networkidle", timeout=timeouts[0])
        return True
    except Exception:
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=timeouts[1])
            return True
        except Exception:
            return False

async def scrape_with_playwright(url: str, max_scrolls: int = 3, max_pages: int = 3):
    interactions = {"clicks": [], "scrolls": 0, "pages": [url]}
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", viewport={"width":1280,"height":720}, ignore_https_errors=True)
        page = await context.new_page()
        ok = await _safe_goto(page, url)
        if not ok:
            final_html = await page.content()
            meta = {"title": "", "description": "", "language": "", "canonical": ""}
            await context.close()
            await browser.close()
            return final_html, meta, interactions

        try:
            await page.evaluate("""() => {
              const blacklist = ['.cookie', '.cookie-banner', '#cookie-consent', '.modal', '.newsletter-popup', '.overlay'];
              blacklist.forEach(s => document.querySelectorAll(s).forEach(el => el.remove()));
            }""")
        except Exception:
            pass

        try:
            tabs = await page.query_selector_all('[role="tab"], button[aria-controls]')
            for t in tabs[:3]:
                try:
                    await t.click(timeout=5000)
                    interactions["clicks"].append("tab clicked")
                    await page.wait_for_timeout(500)
                except Exception:
                    continue
        except Exception:
            pass

        try:
            for _ in range(2):
                load_more = await page.query_selector('button:has-text("Load more"), button:has-text("Show more"), a:has-text("Load more")')
                if not load_more:
                    break
                try:
                    await load_more.click(timeout=5000)
                    interactions["clicks"].append("load-more clicked")
                    await page.wait_for_timeout(1000)
                except Exception:
                    break
        except Exception:
            pass

        for i in range(max_scrolls):
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                interactions["scrolls"] += 1
                await page.wait_for_timeout(1000 + i*500)
            except Exception:
                break

        # try pagination
        pages_visited = set(interactions["pages"])
        try:
            all_anchors = await page.query_selector_all("a[href]")
            anchor_count = len(all_anchors)
        except Exception:
            all_anchors = []
            anchor_count = 0
        print(f"[pagination] found {anchor_count} anchors on page")

        for _ in range(max_pages - 1):
            try:
                href = None
                source = None
                next_el = await page.query_selector('a[rel="next"]')
                if next_el:
                    href = await next_el.get_attribute("href")
                    source = "rel_next"
                if not href:
                    next_el = await page.query_selector('a:has-text("Next"), a:has-text("next"), a:has-text("More"), a:has-text("more"), a:has-text("Older"), a:has-text("older")')
                    if next_el:
                        href = await next_el.get_attribute("href")
                        source = "text_next"

                if not href:
                    anchors = await page.query_selector_all("a[href]")
                    for a in anchors:
                        try:
                            h = (await a.get_attribute("href")) or ""
                            t = (await a.inner_text()) or ""
                            if re.search(r'(\bpage=|\?p=|/p/|\bpg=)', h, re.I) or re.search(r'\b(next|more|older|>\s*>)\b', t, re.I):
                                href = h
                                source = "heuristic_anchor"
                                break
                        except Exception:
                            continue
                if not href:
                    load_more = await page.query_selector('button:has-text("Load more"), button:has-text("Show more"), a:has-text("Load more"), a:has-text("Show more")')
                    if load_more:
                        try:
                            prev_len = await page.evaluate("document.body.innerHTML.length")
                            await load_more.click(timeout=5000)
                            interactions["clicks"].append("load-more clicked")
                            await page.wait_for_timeout(1000)
                            for _w in range(8):
                                cur_len = await page.evaluate("document.body.innerHTML.length")
                                if cur_len > prev_len + 50:
                                    print("[pagination] load-more produced new content")
                                    break
                                await page.wait_for_timeout(250)
                            continue
                        except Exception as e:
                            print("[pagination] load-more click failed:", e)

                if not href:
                    print("[pagination] no candidate href found, stopping")
                    break

                next_url = urljoin(url, href)
                if next_url in pages_visited:
                    break

                if not _is_same_origin(next_url, url):
                    break

                ok = await _safe_goto(page, next_url)
                if not ok:
                    try:
                        await page.goto(next_url, wait_until="domcontentloaded", timeout=15000)
                    except Exception as e:
                        break

                await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                await page.wait_for_timeout(800)

                interactions["pages"].append(next_url)
                pages_visited.add(next_url)

            except Exception as e:
                print("[pagination] exception:", e)
                break

        final_html = await page.content()
        try:
            meta = await page.evaluate("""() => {
                const get = s => {
                  const el = document.querySelector(s);
                  return el && (el.content || el.href) ? (el.content || el.href) : '';
                };
                return {
                  title: document.title || '',
                  description: get('meta[name=\"description\"]') || get('meta[property=\"og:description\"]') || '',
                  language: document.documentElement.lang || '',
                  canonical: get('link[rel=\"canonical\"]') || ''
                }
            }""")
        except Exception:
            meta = {"title": "", "description": "", "language": "", "canonical": ""}

        await context.close()
        await browser.close()
    return final_html, meta, interactions
