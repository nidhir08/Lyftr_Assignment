from bs4 import BeautifulSoup
from urllib.parse import urljoin
import hashlib

def make_id(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]

def text_from_node(node):
    return " ".join(node.stripped_strings)

def extract_links(el, base_url):
    links = []
    for a in el.find_all("a", href=True):
        href = a.get("href", "").strip()
        if not href:
            continue
        links.append({"text": a.get_text(strip=True) or "", "href": urljoin(base_url, href)})
    return links

def extract_images(el, base_url):
    images = []
    for img in el.find_all("img", src=True):
        src = img.get("src", "").strip()
        if not src:
            continue
        images.append({"src": urljoin(base_url, src), "alt": img.get("alt", "")})
    return images

def extract_lists(el):
    lists = []
    for ul in el.find_all(["ul","ol"]):
        items = [li.get_text(strip=True) for li in ul.find_all("li")]
        if items:
            lists.append(items)
    return lists

def extract_tables(el):
    tables = []
    for table in el.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td","th"])]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables

def make_section_from_element(el, base_url, suggested_type="section"):
    html_snip = str(el)[:4000]
    headings = [h.get_text(strip=True) for h in el.find_all(["h1","h2","h3"])][:5]
    txt = text_from_node(el).strip()
    label = headings[0] if headings else (" ".join(txt.split()[:7]) if txt else "Section")
    sec = {
        "id": make_id(label + (txt[:50] if txt else "")),
        "type": suggested_type,
        "label": label,
        "sourceUrl": base_url,
        "content": {
            "headings": headings,
            "text": txt,
            "links": extract_links(el, base_url),
            "images": extract_images(el, base_url),
            "lists": extract_lists(el),
            "tables": extract_tables(el)
        },
        "rawHtml": html_snip,
        "truncated": len(html_snip) >= 4000
    }
    return sec

def parse_sections(html: str, base_url: str):
    soup = BeautifulSoup(html, "lxml")
    sections = []

    # 1)Try landmarks first (header, nav, main, section, article, footer)
    landmarks = soup.find_all(["main","article","section","header","nav","footer"])
    if landmarks:
        for el in landmarks:
            sec = make_section_from_element(el, base_url, suggested_type=("nav" if el.name=="nav" else ("footer" if el.name=="footer" else "section")))
            cont = sec["content"]
            if cont["text"] or cont["links"] or cont["images"] or cont["lists"] or cont["tables"]:
                sections.append(sec)

    # 2)Fallback: group by h1-h3 headings
    if not sections:
        headings = soup.find_all(["h1","h2","h3"])
        for h in headings:
            nodes = []
            for sib in h.next_siblings:
                if getattr(sib, "name", None) in ["h1","h2","h3"]:
                    break
                nodes.append(sib)
            tmp_html = "".join(str(n) for n in nodes)
            tmp_soup = BeautifulSoup(tmp_html, "lxml")
            txt = " ".join(n.get_text(strip=True) for n in nodes if hasattr(n, "get_text")).strip()
            links = extract_links(tmp_soup, base_url)
            images = extract_images(tmp_soup, base_url)
            lists = extract_lists(tmp_soup)
            tables = extract_tables(tmp_soup)
            if txt or links or images or lists or tables:
                sec = {
                    "id": make_id(h.get_text(strip=True) + (txt[:50] if txt else "")),
                    "type": "section",
                    "label": h.get_text(strip=True) or "Section",
                    "sourceUrl": base_url,
                    "content": {
                        "headings": [h.get_text(strip=True)],
                        "text": txt,
                        "links": links,
                        "images": images,
                        "lists": lists,
                        "tables": tables
                    },
                    "rawHtml": (str(h) + tmp_html)[:4000],
                    "truncated": len((str(h)+tmp_html)) >= 4000
                }
                sections.append(sec)

    # 3)Fallback: detect list/article containers (tables, divs, ol/ul, article)
    if not sections:
        candidates = soup.find_all(["table","div","ol","ul","article"])
        for c in candidates:
            txt = text_from_node(c).strip()
            if len(txt) > 120:
                sec = make_section_from_element(c, base_url, suggested_type="list")
                sections.append(sec)
                if len(sections) >= 4:
                    break

    if not sections:
        body = soup.body or soup
        txt = text_from_node(body).strip()
        sec = {
            "id": make_id(base_url),
            "type": "unknown",
            "label": "Main",
            "sourceUrl": base_url,
            "content": {
                "headings": [],
                "text": txt,
                "links": extract_links(body, base_url),
                "images": extract_images(body, base_url),
                "lists": extract_lists(body),
                "tables": extract_tables(body)
            },
            "rawHtml": str(body)[:4000],
            "truncated": len(str(body)) >= 4000
        }
        sections.append(sec)

    return sections
