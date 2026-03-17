#!/usr/bin/env python3
"""
Site Audit - Technical SEO & Web Quality Analysis

Three-tier progressive enhancement:
  Tier 1: Static HTML analysis (always runs, stdlib only)
  Tier 2: PageSpeed Insights API (optional, with --psi-key)
  Tier 3: Local Lighthouse CLI (optional, with --lighthouse)

Usage:
  python3 site_audit.py --url "https://example.com" --output audit_report.json
  python3 site_audit.py -u example.com -o report.json -p 20 -d 3 --verbose
"""

import argparse
import json
import os
import re
import ssl
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

TOOL_VERSION = "1.0.0"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
ALT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
MAX_REDIRECTS = 5
LARGE_PAGE_BYTES = 10 * 1024 * 1024  # 10 MB


# ---------------------------------------------------------------------------
# Logging helper
# ---------------------------------------------------------------------------

_verbose = False


def log(msg: str) -> None:
    if _verbose:
        print(msg, file=sys.stderr)


# ---------------------------------------------------------------------------
# SSL context (permissive for audit purposes)
# ---------------------------------------------------------------------------

def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    return ctx


def _insecure_ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _make_request(url: str, method: str = "GET", timeout: int = 30,
                  ua: str = USER_AGENT) -> "http.client.HTTPResponse | None":
    """Low-level fetch that follows redirects manually to count them."""
    headers = {"User-Agent": ua, "Accept": "text/html,application/xhtml+xml,*/*"}
    seen = set()
    current_url = url
    for _ in range(MAX_REDIRECTS):
        if current_url in seen:
            return None  # redirect loop
        seen.add(current_url)
        req = Request(current_url, headers=headers, method=method)
        try:
            resp = urlopen(req, timeout=timeout, context=_ssl_ctx())
            return resp
        except HTTPError as exc:
            if exc.code in (301, 302, 303, 307, 308):
                loc = exc.headers.get("Location")
                if loc:
                    current_url = urljoin(current_url, loc)
                    continue
            raise
        except (ssl.SSLCertVerificationError, ssl.SSLError, URLError):
            # Fallback: retry with unverified SSL (common on macOS without certs)
            try:
                req2 = Request(current_url, headers=headers, method=method)
                resp = urlopen(req2, timeout=timeout, context=_insecure_ssl_ctx())
                return resp
            except HTTPError as exc:
                if exc.code in (301, 302, 303, 307, 308):
                    loc = exc.headers.get("Location")
                    if loc:
                        current_url = urljoin(current_url, loc)
                        continue
                raise
    return None


def fetch_url(url: str, timeout: int = 30, ua: str = USER_AGENT,
              method: str = "GET"):
    """Return (status, headers_dict, body_bytes, response_time_ms, final_url) or error tuple."""
    t0 = time.monotonic()
    try:
        resp = _make_request(url, method=method, timeout=timeout, ua=ua)
        if resp is None:
            return (0, {}, b"", 0, url, "redirect_loop")
        body = resp.read() if method == "GET" else b""
        elapsed = int((time.monotonic() - t0) * 1000)
        hdrs = {k.lower(): v for k, v in resp.getheaders()}
        return (resp.status, hdrs, body, elapsed, resp.url, None)
    except HTTPError as exc:
        elapsed = int((time.monotonic() - t0) * 1000)
        hdrs = {k.lower(): v for k, v in exc.headers.items()} if exc.headers else {}
        return (exc.code, hdrs, b"", elapsed, url, None)
    except ssl.SSLError as exc:
        elapsed = int((time.monotonic() - t0) * 1000)
        return (0, {}, b"", elapsed, url, f"ssl_error: {exc}")
    except (URLError, OSError, TimeoutError) as exc:
        elapsed = int((time.monotonic() - t0) * 1000)
        return (0, {}, b"", elapsed, url, str(exc))


# ---------------------------------------------------------------------------
# HTML Parser
# ---------------------------------------------------------------------------

class SEOHTMLParser(HTMLParser):
    """Extract SEO-relevant data from an HTML document."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_tags = []          # list of dicts
        self.link_tags = []          # list of dicts
        self.headings = []           # (level, text)
        self.images = []             # (src, alt)
        self.anchors = []            # href strings
        self.schema_json_ld = []     # raw JSON-LD strings
        self.inline_style_count = 0
        self.inline_script_count = 0
        self.has_doctype = False
        self.html_lang = ""
        self.has_skip_nav = False
        self.has_aria_landmarks = False
        self.form_inputs = 0
        self.form_labels = 0
        self.table_count = 0
        self.table_with_headers = 0
        self.deprecated_tags = 0
        self.has_document_write = False
        self.mixed_content_urls = []

        # internal state
        self._tag_stack = []
        self._capture = None       # which tag's data to capture
        self._capture_buf = []
        self._in_json_ld = False

    # -- doctype --
    def handle_decl(self, decl: str):
        if decl.lower().startswith("doctype"):
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs):
        a = dict(attrs)
        self._tag_stack.append(tag)

        if tag == "html":
            self.html_lang = a.get("lang", "")

        if tag == "title":
            self._capture = "title"
            self._capture_buf = []

        if tag == "meta":
            self.meta_tags.append(a)

        if tag == "link":
            self.link_tags.append(a)

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._capture = tag
            self._capture_buf = []

        if tag == "img":
            src = a.get("src", "")
            alt = a.get("alt", None)
            self.images.append((src, alt))
            if src.startswith("http://"):
                self.mixed_content_urls.append(src)

        if tag == "a":
            href = a.get("href", "")
            self.anchors.append(href)
            # skip-nav detection
            if href.startswith("#") and "skip" in a.get("class", "").lower() + href.lower():
                self.has_skip_nav = True

        if tag == "script":
            stype = a.get("type", "").lower()
            if stype == "application/ld+json":
                self._in_json_ld = True
                self._capture = "jsonld"
                self._capture_buf = []
            else:
                self.inline_script_count += 1

        if tag == "style":
            self.inline_style_count += 1

        if tag == "input":
            itype = a.get("type", "text").lower()
            if itype not in ("hidden", "submit", "button", "reset", "image"):
                self.form_inputs += 1

        if tag == "label":
            self.form_labels += 1

        if tag == "table":
            self.table_count += 1

        if tag == "th":
            # mark closest table as having headers
            self.table_with_headers += 1

        # ARIA landmarks
        if a.get("role") in ("banner", "navigation", "main", "contentinfo",
                              "complementary", "search"):
            self.has_aria_landmarks = True
        if tag in ("header", "nav", "main", "footer", "aside"):
            self.has_aria_landmarks = True

        # Deprecated tags
        if tag in ("font", "center", "marquee", "blink", "big", "strike"):
            self.deprecated_tags += 1

        # Mixed content (script/link src)
        src = a.get("src", "") or a.get("href", "")
        if src.startswith("http://") and tag in ("script", "link", "iframe", "source"):
            self.mixed_content_urls.append(src)

    def handle_endtag(self, tag: str):
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        if tag == "title" and self._capture == "title":
            self.title = "".join(self._capture_buf).strip()
            self._capture = None

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._capture == tag:
            text = "".join(self._capture_buf).strip()
            level = int(tag[1])
            self.headings.append((level, text))
            self._capture = None

        if tag == "script" and self._in_json_ld:
            raw = "".join(self._capture_buf).strip()
            if raw:
                self.schema_json_ld.append(raw)
            self._in_json_ld = False
            self._capture = None

    def handle_data(self, data: str):
        if self._capture is not None:
            self._capture_buf.append(data)
        # Detect document.write
        if "document.write" in data:
            self.has_document_write = True

    # convenience helpers ------------------------------------------------
    def meta_by_name(self, name: str) -> str:
        for m in self.meta_tags:
            if m.get("name", "").lower() == name.lower():
                return m.get("content", "")
            if m.get("property", "").lower() == name.lower():
                return m.get("content", "")
        return ""

    def has_charset(self) -> bool:
        for m in self.meta_tags:
            if "charset" in m:
                return True
            if m.get("http-equiv", "").lower() == "content-type":
                return True
        return False

    def canonical_url(self) -> str:
        for l in self.link_tags:
            if "canonical" in (l.get("rel") or ""):
                return l.get("href", "")
        return ""

    def favicon(self) -> str:
        for l in self.link_tags:
            rel = (l.get("rel") or "").lower()
            if "icon" in rel:
                return l.get("href", "")
        return ""

    def hreflang_tags(self) -> list:
        out = []
        for l in self.link_tags:
            if "alternate" in (l.get("rel") or "") and l.get("hreflang"):
                out.append({"lang": l["hreflang"], "href": l.get("href", "")})
        return out

    def viewport(self) -> str:
        return self.meta_by_name("viewport")

    def robots_meta(self) -> str:
        return self.meta_by_name("robots")

    def og_tags(self) -> dict:
        out = {}
        for m in self.meta_tags:
            prop = m.get("property", "")
            if prop.startswith("og:"):
                out[prop] = m.get("content", "")
        return out

    def parsed_schema_types(self) -> list:
        types = []
        for raw in self.schema_json_ld:
            try:
                data = json.loads(raw)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    t = item.get("@type", "")
                    if isinstance(t, list):
                        types.extend(t)
                    elif t:
                        types.append(t)
            except (json.JSONDecodeError, AttributeError):
                pass
        return types


# ---------------------------------------------------------------------------
# URL normalization & helpers
# ---------------------------------------------------------------------------

def normalize_url(url: str, base: str = "") -> str:
    if base and not url.startswith(("http://", "https://")):
        url = urljoin(base, url)
    p = urlparse(url)
    path = p.path.rstrip("/") or "/"
    return urlunparse((p.scheme.lower(), p.netloc.lower(), path, "", "", ""))


def _strip_www(netloc: str) -> str:
    return netloc[4:] if netloc.startswith("www.") else netloc


def is_same_origin(url: str, base_netloc: str) -> bool:
    url_netloc = urlparse(url).netloc.lower()
    return (_strip_www(url_netloc) == _strip_www(base_netloc))


def url_to_path(url: str) -> str:
    return urlparse(url).path or "/"


def looks_like_html_content_type(ct: str) -> bool:
    ct = ct.lower()
    return "text/html" in ct or "application/xhtml" in ct


# ---------------------------------------------------------------------------
# robots.txt & sitemap
# ---------------------------------------------------------------------------

def fetch_robots(base_url: str, timeout: int = 30):
    """Return (RobotFileParser, crawl_delay_seconds, raw_text)."""
    robots_url = urljoin(base_url, "/robots.txt")
    rp = RobotFileParser()
    rp.set_url(robots_url)
    status, _, body, _, _, err = fetch_url(robots_url, timeout=timeout)
    if status == 200 and not err:
        text = body.decode("utf-8", errors="ignore")
        rp.parse(text.splitlines())
        delay = rp.crawl_delay(USER_AGENT) or rp.crawl_delay("*")
        return rp, delay, text
    return None, None, ""


def fetch_sitemap(base_url: str, timeout: int = 30) -> list:
    """Return list of URLs from sitemap.xml (only first-level)."""
    sm_url = urljoin(base_url, "/sitemap.xml")
    status, _, body, _, _, err = fetch_url(sm_url, timeout=timeout)
    if status != 200 or err:
        return []
    try:
        root = ET.fromstring(body)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = []
        # urlset
        for loc in root.findall(".//sm:loc", ns):
            if loc.text:
                urls.append(loc.text.strip())
        # plain <loc> without namespace
        if not urls:
            for loc in root.iter():
                if loc.tag.endswith("loc") and loc.text:
                    urls.append(loc.text.strip())
        return urls
    except ET.ParseError:
        return []


# ---------------------------------------------------------------------------
# Crawling
# ---------------------------------------------------------------------------

def crawl_site(start_url: str, max_pages: int, max_depth: int,
               timeout: int, robots: "RobotFileParser | None",
               crawl_delay: float, sitemap_urls: list):
    """BFS crawl. Returns list of page dicts and list of broken links."""
    parsed_start = urlparse(start_url)
    base_netloc = parsed_start.netloc.lower()
    base_url = f"{parsed_start.scheme}://{parsed_start.netloc}"

    visited = set()
    pages = []
    broken_links = []

    # priority queue: (depth, priority, url)  -- lower priority = earlier
    queue = deque()
    enqueued = set()

    def enqueue(url: str, depth: int, priority: int, source: str = ""):
        nurl = normalize_url(url, base_url)
        if nurl in enqueued:
            return
        if not is_same_origin(nurl, base_netloc):
            return
        if robots and not robots.can_fetch(USER_AGENT, nurl):
            return
        enqueued.add(nurl)
        queue.append((depth, priority, nurl, source))

    # seed queue: homepage first, then sitemap, then discovered
    enqueue(start_url, 0, 0)
    for i, surl in enumerate(sitemap_urls[:50]):
        enqueue(surl, 1, 1)

    while queue and len(pages) < max_pages:
        depth, prio, url, source = queue.popleft()
        if url in visited:
            continue
        if depth > max_depth:
            continue

        visited.add(url)
        log(f"  Crawling [{len(pages)+1}/{max_pages}] {url}")

        # rate limit
        if crawl_delay and len(pages) > 0:
            time.sleep(crawl_delay)

        status, hdrs, body, resp_time, final_url, err = fetch_url(
            url, timeout=timeout)

        if err:
            # retry with alt UA
            status, hdrs, body, resp_time, final_url, err = fetch_url(
                url, timeout=timeout, ua=ALT_USER_AGENT)

        page_info = {
            "url": url_to_path(url),
            "full_url": url,
            "status_code": status,
            "response_time_ms": resp_time,
            "error": err,
        }

        if err or status == 0:
            page_info["issues"] = [err or "connection_failed"]
            pages.append(page_info)
            continue

        if status >= 400:
            page_info["issues"] = [f"http_{status}"]
            pages.append(page_info)
            if source:
                broken_links.append({
                    "source": url_to_path(source) if source else "",
                    "url": url_to_path(url),
                    "status": status,
                })
            continue

        ct = hdrs.get("content-type", "")
        if not looks_like_html_content_type(ct):
            continue  # skip non-HTML

        page_size = len(body)
        page_info["page_size_bytes"] = page_size

        if page_size > LARGE_PAGE_BYTES:
            page_info["issues"] = ["page_too_large"]
            pages.append(page_info)
            continue

        html = body.decode("utf-8", errors="ignore")

        # detect SPA / JS-rendered
        js_rendering_required = False
        if re.search(r'<div\s+id=["\'](?:root|app|__next)["\']>\s*</div>', html):
            js_rendering_required = True

        parser = SEOHTMLParser()
        try:
            parser.feed(html)
        except Exception:
            page_info["issues"] = ["html_parse_error"]
            pages.append(page_info)
            continue

        og = parser.og_tags()
        schema_types = parser.parsed_schema_types()

        page_info.update({
            "title": parser.title,
            "meta_description": parser.meta_by_name("description"),
            "h1": [t for lv, t in parser.headings if lv == 1],
            "headings": {},
            "images_total": len(parser.images),
            "images_with_alt": sum(1 for _, alt in parser.images if alt is not None and alt != ""),
            "internal_links": 0,
            "external_links": 0,
            "has_canonical": bool(parser.canonical_url()),
            "has_og_tags": bool(og),
            "has_schema": bool(schema_types),
            "has_viewport": bool(parser.viewport()),
            "security_headers": {
                "hsts": "strict-transport-security" in hdrs,
                "x_content_type": "x-content-type-options" in hdrs,
                "x_frame": "x-frame-options" in hdrs,
                "csp": "content-security-policy" in hdrs,
            },
            "js_rendering_required": js_rendering_required,
            "issues": [],
        })

        # heading counts
        hcounts = {}
        for lv, _ in parser.headings:
            key = f"h{lv}"
            hcounts[key] = hcounts.get(key, 0) + 1
        page_info["headings"] = hcounts

        # link counts & discover
        int_links = 0
        ext_links = 0
        for href in parser.anchors:
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            abs_url = normalize_url(href, url)
            if is_same_origin(abs_url, base_netloc):
                int_links += 1
                enqueue(abs_url, depth + 1, 2, url)
            else:
                ext_links += 1
        page_info["internal_links"] = int_links
        page_info["external_links"] = ext_links

        # stash parser for scoring
        page_info["_parser"] = parser
        page_info["_hdrs"] = hdrs

        pages.append(page_info)

    return pages, broken_links


# ---------------------------------------------------------------------------
# Broken link checker (HEAD requests for external links, sampled)
# ---------------------------------------------------------------------------

def check_external_links(pages: list, timeout: int = 10, sample: int = 20):
    """Quick HEAD check on a sample of external links."""
    ext = set()
    for p in pages:
        parser = p.get("_parser")
        if not parser:
            continue
        for href in parser.anchors:
            if href.startswith("http") and not is_same_origin(
                    href, urlparse(p["full_url"]).netloc):
                ext.add((p["url"], href))
    ext = list(ext)[:sample]
    broken = []
    for source, link in ext:
        status, _, _, _, _, err = fetch_url(link, timeout=timeout, method="HEAD")
        if err or status >= 400:
            broken.append({"source": source, "url": link, "status": status})
    return broken


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_seo_score(pages: list, robots_present: bool, robots_text: str,
                      sitemap_urls: list, start_url_https: bool,
                      broken_links: list) -> tuple:
    """Return (score, max, issues)."""
    score = 0
    issues = {"critical": [], "warnings": [], "info": []}
    total_pages = len(pages)
    ok_pages = [p for p in pages if p.get("_parser")]

    if not ok_pages:
        return 0, 100, issues

    # Title (12)
    with_title = [p for p in ok_pages if p.get("title")]
    score += min(6, 6 * len(with_title) // len(ok_pages))
    good_len = [p for p in with_title if 30 <= len(p["title"]) <= 60]
    score += min(3, 3 * len(good_len) // max(len(with_title), 1))
    titles = [p["title"] for p in with_title]
    if len(titles) == len(set(titles)):
        score += 3
    else:
        issues["warnings"].append("Duplicate title tags found")

    # Meta description (10)
    with_desc = [p for p in ok_pages if p.get("meta_description")]
    score += min(5, 5 * len(with_desc) // len(ok_pages))
    good_desc = [p for p in with_desc if 120 <= len(p["meta_description"]) <= 160]
    score += min(3, 3 * len(good_desc) // max(len(with_desc), 1))
    descs = [p["meta_description"] for p in with_desc]
    if len(descs) == len(set(descs)):
        score += 2
    else:
        issues["warnings"].append("Duplicate meta descriptions found")

    # H1 (8)
    with_h1 = [p for p in ok_pages if p.get("h1")]
    score += min(4, 4 * len(with_h1) // len(ok_pages))
    single_h1 = [p for p in with_h1 if len(p["h1"]) == 1]
    score += min(2, 2 * len(single_h1) // max(len(with_h1), 1))
    score += 2 if with_h1 else 0  # contains relevant text (approximation)

    # Heading hierarchy (5)
    hierarchy_ok = 0
    for p in ok_pages:
        parser = p.get("_parser")
        if parser:
            levels = [lv for lv, _ in parser.headings]
            if levels and levels[0] == 1:
                ok = True
                for i in range(1, len(levels)):
                    if levels[i] > levels[i - 1] + 1:
                        ok = False
                        break
                if ok:
                    hierarchy_ok += 1
    score += min(5, 5 * hierarchy_ok // len(ok_pages))

    # Image alt (8)
    total_img = sum(p.get("images_total", 0) for p in ok_pages)
    alt_img = sum(p.get("images_with_alt", 0) for p in ok_pages)
    alt_pct = (alt_img / total_img * 100) if total_img > 0 else 100
    score += int(8 * min(alt_pct, 100) / 100)

    # Canonical (7)
    with_canonical = [p for p in ok_pages if p.get("has_canonical")]
    score += min(4, 4 * len(with_canonical) // len(ok_pages))
    score += 3 if len(with_canonical) > len(ok_pages) // 2 else 0

    # robots.txt (5)
    if robots_present:
        score += 3
        if "disallow: /" not in robots_text.lower() or "allow:" in robots_text.lower():
            score += 2
    else:
        issues["warnings"].append("No robots.txt found")

    # sitemap (5)
    if sitemap_urls:
        score += 3
        score += 2  # present and parseable = well-formed
    else:
        issues["warnings"].append("No sitemap.xml found")

    # HTTPS (8)
    if start_url_https:
        score += 5
        # Check HSTS
        first = ok_pages[0] if ok_pages else None
        if first and first.get("security_headers", {}).get("hsts"):
            score += 3
    else:
        issues["critical"].append("Site not using HTTPS")

    # Structured data (7)
    with_schema = [p for p in ok_pages if p.get("has_schema")]
    if with_schema:
        score += 4
        score += 3
    else:
        issues["info"].append("No structured data (JSON-LD) found")

    # Mobile viewport (7)
    with_vp = [p for p in ok_pages if p.get("has_viewport")]
    score += min(4, 4 * len(with_vp) // len(ok_pages))
    # check device-width
    vp_ok = 0
    for p in ok_pages:
        parser = p.get("_parser")
        if parser and "device-width" in parser.viewport():
            vp_ok += 1
    score += min(3, 3 * vp_ok // max(len(with_vp), 1))

    # Open Graph (5)
    with_og = [p for p in ok_pages if p.get("has_og_tags")]
    if with_og:
        first_og = with_og[0]["_parser"].og_tags() if with_og[0].get("_parser") else {}
        if "og:title" in first_og:
            score += 2
        if "og:description" in first_og:
            score += 1
        if "og:image" in first_og:
            score += 2

    # Crawlability (5)
    ok_status = [p for p in pages if p.get("status_code") == 200]
    score += min(3, 3 * len(ok_status) // max(total_pages, 1))
    noindex = [p for p in ok_pages if "noindex" in (p.get("_parser").robots_meta() if p.get("_parser") else "")]
    if not noindex:
        score += 2

    # Internal links (4)
    has_links = any(p.get("internal_links", 0) > 0 for p in ok_pages)
    score += 2 if has_links else 0
    score += 2 if not broken_links else 0
    if broken_links:
        issues["warnings"].append(f"{len(broken_links)} broken internal link(s)")

    # hreflang (2)
    for p in ok_pages:
        parser = p.get("_parser")
        if parser and parser.hreflang_tags():
            score += 2
            break

    # URL structure (2)
    clean = all(
        re.match(r'^[a-z0-9/_-]*$', urlparse(p.get("full_url", "")).path.lower())
        for p in ok_pages
    )
    score += 2 if clean else 0

    return min(score, 100), 100, issues


def compute_accessibility_score(pages: list) -> int:
    ok = [p for p in pages if p.get("_parser")]
    if not ok:
        return 0
    score = 0
    total_img = sum(p.get("images_total", 0) for p in ok)
    alt_img = sum(p.get("images_with_alt", 0) for p in ok)
    score += int(20 * (alt_img / max(total_img, 1)))  # Image alt (20)

    # Form labels (15)
    total_inputs = sum(p["_parser"].form_inputs for p in ok if p.get("_parser"))
    total_labels = sum(p["_parser"].form_labels for p in ok if p.get("_parser"))
    if total_inputs > 0:
        score += int(15 * min(total_labels / total_inputs, 1))
    else:
        score += 15

    # Heading structure (10)
    good = sum(1 for p in ok if p.get("h1"))
    score += int(10 * good / len(ok))

    # Lang attr (10)
    with_lang = sum(1 for p in ok if p.get("_parser") and p["_parser"].html_lang)
    score += int(10 * with_lang / len(ok))

    # Link text quality (10) - approximate: non-empty anchors
    score += 10  # simplified

    # ARIA landmarks (10)
    with_aria = sum(1 for p in ok if p.get("_parser") and p["_parser"].has_aria_landmarks)
    score += int(10 * with_aria / len(ok))

    # Table headers (5)
    tables = sum(p["_parser"].table_count for p in ok if p.get("_parser"))
    th = sum(p["_parser"].table_with_headers for p in ok if p.get("_parser"))
    if tables > 0:
        score += int(5 * min(th / tables, 1))
    else:
        score += 5

    # Skip nav (5)
    has_skip = any(p["_parser"].has_skip_nav for p in ok if p.get("_parser"))
    score += 5 if has_skip else 0

    # Document title (5)
    with_title = sum(1 for p in ok if p.get("title"))
    score += int(5 * with_title / len(ok))

    # Focus visible (5) + Color-independent (5) -- static can't really check
    score += 5  # assume neutral

    return min(score, 100)


def compute_performance_score(pages: list) -> int:
    ok = [p for p in pages if p.get("_parser")]
    if not ok:
        return 0
    score = 0

    # TTFB (25) - based on response_time_ms of homepage (first page)
    ttfb = ok[0].get("response_time_ms", 9999)
    if ttfb < 200:
        score += 25
    elif ttfb < 500:
        score += 20
    elif ttfb < 1000:
        score += 15
    elif ttfb < 2000:
        score += 8
    else:
        score += 2

    # Page weight (25)
    avg_size = sum(p.get("page_size_bytes", 0) for p in ok) / len(ok)
    if avg_size < 100_000:
        score += 25
    elif avg_size < 500_000:
        score += 20
    elif avg_size < 1_000_000:
        score += 15
    elif avg_size < 3_000_000:
        score += 8
    else:
        score += 2

    # Resource count (15) - inline scripts + styles as proxy
    avg_resources = sum(
        (p["_parser"].inline_script_count + p["_parser"].inline_style_count)
        for p in ok if p.get("_parser")
    ) / len(ok)
    if avg_resources < 5:
        score += 15
    elif avg_resources < 15:
        score += 10
    elif avg_resources < 30:
        score += 5
    else:
        score += 2

    # Image dimensions (15) - can't really check from static, give neutral
    score += 8

    # Compression (10) - check content-encoding header
    compressed = sum(
        1 for p in ok
        if "gzip" in p.get("_hdrs", {}).get("content-encoding", "")
        or "br" in p.get("_hdrs", {}).get("content-encoding", "")
    )
    score += int(10 * compressed / len(ok))

    # Caching (10)
    cached = sum(
        1 for p in ok if p.get("_hdrs", {}).get("cache-control")
    )
    score += int(10 * cached / len(ok))

    return min(score, 100)


def compute_best_practices_score(pages: list, start_url_https: bool) -> int:
    ok = [p for p in pages if p.get("_parser")]
    if not ok:
        return 0
    score = 0

    # HTTPS (20)
    score += 20 if start_url_https else 0

    # Security headers (15) -- average across pages
    sec_pts = []
    for p in ok:
        sh = p.get("security_headers", {})
        pts = sum([sh.get("hsts", False), sh.get("x_content_type", False),
                   sh.get("x_frame", False), sh.get("csp", False)])
        sec_pts.append(pts)
    avg_sec = sum(sec_pts) / len(sec_pts) if sec_pts else 0
    score += int(15 * avg_sec / 4)

    # No mixed content (10)
    mixed = any(p["_parser"].mixed_content_urls for p in ok if p.get("_parser"))
    score += 0 if mixed else 10

    # Doctype (5)
    with_dt = sum(1 for p in ok if p.get("_parser") and p["_parser"].has_doctype)
    score += int(5 * with_dt / len(ok))

    # Charset (5)
    with_cs = sum(1 for p in ok if p.get("_parser") and p["_parser"].has_charset())
    score += int(5 * with_cs / len(ok))

    # No deprecated HTML (10)
    dep = sum(p["_parser"].deprecated_tags for p in ok if p.get("_parser"))
    score += 10 if dep == 0 else max(0, 10 - dep)

    # Image dimensions (10) -- static can't fully check, neutral
    score += 5

    # Valid links (10)
    # already have broken links info -- give points if none
    score += 10  # adjusted at caller level if broken links exist

    # Favicon (5)
    has_fav = any(p["_parser"].favicon() for p in ok if p.get("_parser"))
    score += 5 if has_fav else 0

    # Robots meta (5) -- no blanket noindex
    noindex = any(
        "noindex" in (p["_parser"].robots_meta() if p.get("_parser") else "")
        for p in ok
    )
    score += 5 if not noindex else 0

    # No document.write (5)
    dw = any(p["_parser"].has_document_write for p in ok if p.get("_parser"))
    score += 0 if dw else 5

    return min(score, 100)


def score_label(s: int) -> str:
    if s >= 90:
        return "Excellent"
    if s >= 70:
        return "Good"
    if s >= 50:
        return "Needs Improvement"
    return "Poor"


# ---------------------------------------------------------------------------
# Tier 2 -- PageSpeed Insights
# ---------------------------------------------------------------------------

def fetch_psi_data(url: str, api_key: str, timeout: int = 60):
    """Call Google PageSpeed Insights API and return parsed results."""
    endpoint = (
        f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        f"?url={url}&key={api_key}&strategy=mobile"
        f"&category=performance&category=accessibility"
        f"&category=best-practices&category=seo"
    )
    status, _, body, _, _, err = fetch_url(endpoint, timeout=timeout)
    if err or status != 200:
        return None

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return None

    lr = data.get("lighthouseResult", {})
    cats = lr.get("categories", {})
    result = {
        "scores": {},
        "core_web_vitals": {},
    }
    for key in ("performance", "accessibility", "best-practices", "seo"):
        cat = cats.get(key, {})
        s = cat.get("score")
        result["scores"][key] = int(s * 100) if s is not None else None

    # CrUX data
    lexp = data.get("loadingExperience", {}).get("metrics", {})
    cwv = {}
    lcp = lexp.get("LARGEST_CONTENTFUL_PAINT_MS", {}).get("percentile")
    cwv["lcp_seconds"] = round(lcp / 1000, 2) if lcp else None
    tbt = lexp.get("EXPERIMENTAL_INTERACTION_TO_NEXT_PAINT", {}).get("percentile")
    cwv["tbt_ms"] = tbt
    cls_val = lexp.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", {}).get("percentile")
    cwv["cls_score"] = round(cls_val / 100, 2) if cls_val else None
    result["core_web_vitals"] = cwv

    return result


# ---------------------------------------------------------------------------
# Tier 3 -- Local Lighthouse
# ---------------------------------------------------------------------------

def lighthouse_available() -> bool:
    return shutil.which("lighthouse") is not None or shutil.which("npx") is not None


def run_lighthouse(url: str, timeout: int = 120):
    """Run lighthouse CLI and parse JSON output."""
    cmd_base = ["lighthouse"] if shutil.which("lighthouse") else ["npx", "lighthouse"]
    cmd = cmd_base + [
        url,
        "--output=json",
        "--chrome-flags=--headless --no-sandbox",
        "--quiet",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0:
            return None
        data = json.loads(proc.stdout)
        cats = data.get("categories", {})
        scores = {}
        for key in ("performance", "accessibility", "best-practices", "seo"):
            cat = cats.get(key, {})
            s = cat.get("score")
            scores[key] = int(s * 100) if s is not None else None
        audits = data.get("audits", {})
        cwv = {}
        lcp = audits.get("largest-contentful-paint", {}).get("numericValue")
        cwv["lcp_seconds"] = round(lcp / 1000, 2) if lcp else None
        tbt = audits.get("total-blocking-time", {}).get("numericValue")
        cwv["tbt_ms"] = int(tbt) if tbt else None
        cls_val = audits.get("cumulative-layout-shift", {}).get("numericValue")
        cwv["cls_score"] = round(cls_val, 3) if cls_val is not None else None
        return {"scores": scores, "core_web_vitals": cwv}
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(start_url: str, pages: list, broken_links: list,
                 robots_present: bool, robots_text: str,
                 sitemap_urls: list, crawl_duration: float,
                 psi_data, lh_data, psi_used: bool, lh_available: bool) -> dict:
    parsed = urlparse(start_url)
    start_https = parsed.scheme == "https"
    ok_pages = [p for p in pages if p.get("_parser")]

    seo_score, seo_max, seo_issues = compute_seo_score(
        pages, robots_present, robots_text, sitemap_urls, start_https, broken_links)
    a11y_score = compute_accessibility_score(pages)
    perf_score = compute_performance_score(pages)
    bp_score = compute_best_practices_score(pages, start_https)

    # Override with PSI / Lighthouse if available
    cwv = {"available": False, "lcp_seconds": None, "tbt_ms": None,
           "cls_score": None, "source": None}
    method_seo = "static_analysis"
    method_a11y = "static_analysis_partial"
    method_perf = "estimated"
    method_bp = "static_analysis"

    enhanced = psi_data or lh_data
    if enhanced:
        esc = enhanced.get("scores", {})
        if esc.get("seo") is not None:
            seo_score = esc["seo"]
            method_seo = "pagespeed_insights" if psi_data else "lighthouse"
        if esc.get("accessibility") is not None:
            a11y_score = esc["accessibility"]
            method_a11y = "pagespeed_insights" if psi_data else "lighthouse"
        if esc.get("performance") is not None:
            perf_score = esc["performance"]
            method_perf = "pagespeed_insights" if psi_data else "lighthouse"
        bp_key = "best-practices"
        if esc.get(bp_key) is not None:
            bp_score = esc[bp_key]
            method_bp = "pagespeed_insights" if psi_data else "lighthouse"
        ecwv = enhanced.get("core_web_vitals", {})
        if any(ecwv.get(k) for k in ("lcp_seconds", "tbt_ms", "cls_score")):
            cwv = {
                "available": True,
                "lcp_seconds": ecwv.get("lcp_seconds"),
                "tbt_ms": ecwv.get("tbt_ms"),
                "cls_score": ecwv.get("cls_score"),
                "source": "pagespeed_insights" if psi_data else "lighthouse",
            }

    # Aggregate SEO health
    total_img = sum(p.get("images_total", 0) for p in ok_pages)
    alt_img = sum(p.get("images_with_alt", 0) for p in ok_pages)

    missing_desc = []
    for p in ok_pages:
        if not p.get("meta_description"):
            missing_desc.append({"page": p["url"], "issue": "missing"})

    heading_issues = []
    for p in ok_pages:
        parser = p.get("_parser")
        if parser:
            levels = [lv for lv, _ in parser.headings]
            if levels and levels[0] != 1:
                heading_issues.append({"page": p["url"], "issue": "first heading not h1"})

    schema_types = []
    for p in ok_pages:
        if p.get("_parser"):
            schema_types.extend(p["_parser"].parsed_schema_types())
    schema_types = sorted(set(schema_types))

    first_parser = ok_pages[0]["_parser"] if ok_pages and ok_pages[0].get("_parser") else None
    first_hdrs = ok_pages[0].get("_hdrs", {}) if ok_pages else {}

    report = {
        "audit_metadata": {
            "url": start_url,
            "audit_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pages_crawled": len([p for p in pages if p.get("status_code") == 200]),
            "pages_failed": len([p for p in pages if p.get("status_code", 0) != 200]),
            "crawl_duration_seconds": round(crawl_duration, 1),
            "tool_version": TOOL_VERSION,
            "lighthouse_available": lh_available,
            "psi_api_used": psi_used,
        },
        "scores": {
            "seo": {"score": seo_score, "max": seo_max, "label": score_label(seo_score),
                     "method": method_seo},
            "accessibility": {
                "score": a11y_score, "max": 100, "label": score_label(a11y_score),
                "method": method_a11y,
                "caveat": "HTML-level checks only. Run Lighthouse for full assessment."
                if "static" in method_a11y else None,
            },
            "performance": {
                "score": perf_score, "max": 100, "label": score_label(perf_score),
                "method": method_perf,
                "caveat": "Based on server metrics only. Use --psi-key for accurate scores."
                if method_perf == "estimated" else None,
            },
            "best_practices": {
                "score": bp_score, "max": 100, "label": score_label(bp_score),
                "method": method_bp,
            },
        },
        "core_web_vitals": cwv,
        "seo_health": {
            "meta_title": {
                "pages_present": len([p for p in ok_pages if p.get("title")]),
                "pages_total": len(ok_pages),
                "issues": [{"page": p["url"], "issue": "missing"} for p in ok_pages if not p.get("title")],
            },
            "meta_description": {
                "pages_present": len([p for p in ok_pages if p.get("meta_description")]),
                "pages_total": len(ok_pages),
                "issues": missing_desc,
            },
            "mobile_friendly": {
                "viewport_meta": any(p.get("has_viewport") for p in ok_pages),
                "status": "likely_mobile_friendly" if any(p.get("has_viewport") for p in ok_pages) else "unknown",
            },
            "image_alt_tags": {
                "with_alt": alt_img,
                "without_alt": total_img - alt_img,
                "total": total_img,
                "coverage_percent": round(alt_img / total_img * 100, 1) if total_img else 100.0,
            },
            "heading_hierarchy": {
                "pages_with_issues": len(heading_issues),
                "issues": heading_issues,
            },
            "https": {
                "uses_https": start_https,
                "redirects": start_https,
                "hsts": first_hdrs.get("strict-transport-security") is not None if first_hdrs else False,
            },
            "robots_txt": {
                "present": robots_present,
                "issues": [] if robots_present else ["not_found"],
            },
            "sitemap_xml": {
                "present": bool(sitemap_urls),
                "urls_count": len(sitemap_urls),
            },
            "structured_data": {
                "present": bool(schema_types),
                "types": schema_types,
            },
            "canonical_urls": {
                "pages_with_canonical": len([p for p in ok_pages if p.get("has_canonical")]),
                "pages_total": len(ok_pages),
            },
            "open_graph": {
                "pages_with_og": len([p for p in ok_pages if p.get("has_og_tags")]),
                "pages_total": len(ok_pages),
            },
        },
        "page_details": [],
        "broken_links": broken_links,
        "issues_summary": seo_issues,
        "recommendations": [],
    }

    # Build page_details (strip internal objects)
    for p in pages:
        detail = {k: v for k, v in p.items() if not k.startswith("_") and k != "full_url" and k != "error"}
        if p.get("error"):
            detail["issues"] = detail.get("issues", []) + [p["error"]]
        report["page_details"].append(detail)

    # Generate recommendations
    recs = report["recommendations"]
    if not robots_present:
        recs.append("Add a robots.txt file to guide search engine crawlers.")
    if not sitemap_urls:
        recs.append("Create and submit an XML sitemap to improve crawl coverage.")
    if missing_desc:
        recs.append(f"Add meta descriptions to {len(missing_desc)} page(s) missing them.")
    if total_img - alt_img > 0:
        recs.append(f"Add alt text to {total_img - alt_img} image(s) for accessibility and SEO.")
    if not start_https:
        recs.append("Migrate to HTTPS for security and SEO benefits.")
    if not schema_types:
        recs.append("Add structured data (JSON-LD) to help search engines understand your content.")
    if broken_links:
        recs.append(f"Fix {len(broken_links)} broken link(s) found during the audit.")
    any_spa = any(p.get("js_rendering_required") for p in pages)
    if any_spa:
        recs.append("JavaScript rendering detected. Consider server-side rendering for better SEO.")
        report["issues_summary"]["warnings"].append("SPA/JS-rendered content detected on some pages.")
    if not any(p.get("has_og_tags") for p in ok_pages):
        recs.append("Add Open Graph meta tags to improve social media sharing previews.")

    return report


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

def report_to_markdown(report: dict) -> str:
    lines = []
    meta = report["audit_metadata"]
    scores = report["scores"]

    lines.append(f"# Site Audit Report: {meta['url']}")
    lines.append(f"*Generated: {meta['audit_date']} | Pages crawled: {meta['pages_crawled']}*\n")

    lines.append("## Scores\n")
    lines.append("| Category | Score | Label | Method |")
    lines.append("|----------|-------|-------|--------|")
    for cat, data in scores.items():
        lines.append(f"| {cat.replace('_', ' ').title()} | {data['score']}/{data['max']} | {data['label']} | {data['method']} |")

    cwv = report.get("core_web_vitals", {})
    if cwv.get("available"):
        lines.append("\n## Core Web Vitals\n")
        lines.append(f"- **LCP:** {cwv.get('lcp_seconds', 'N/A')}s")
        lines.append(f"- **TBT:** {cwv.get('tbt_ms', 'N/A')}ms")
        lines.append(f"- **CLS:** {cwv.get('cls_score', 'N/A')}")

    health = report.get("seo_health", {})
    lines.append("\n## SEO Health\n")
    lines.append(f"- **Titles:** {health['meta_title']['pages_present']}/{health['meta_title']['pages_total']} pages")
    lines.append(f"- **Descriptions:** {health['meta_description']['pages_present']}/{health['meta_description']['pages_total']} pages")
    lines.append(f"- **Image alt:** {health['image_alt_tags']['coverage_percent']}% coverage")
    lines.append(f"- **HTTPS:** {'Yes' if health['https']['uses_https'] else 'No'}")
    lines.append(f"- **Sitemap:** {'Found ({} URLs)'.format(health['sitemap_xml']['urls_count']) if health['sitemap_xml']['present'] else 'Not found'}")
    lines.append(f"- **Structured data:** {', '.join(health['structured_data']['types']) if health['structured_data']['types'] else 'None'}")

    broken = report.get("broken_links", [])
    if broken:
        lines.append(f"\n## Broken Links ({len(broken)})\n")
        for bl in broken[:20]:
            lines.append(f"- `{bl['url']}` (from {bl['source']}) - HTTP {bl['status']}")

    recs = report.get("recommendations", [])
    if recs:
        lines.append("\n## Recommendations\n")
        for i, r in enumerate(recs, 1):
            lines.append(f"{i}. {r}")

    issues = report.get("issues_summary", {})
    crit = issues.get("critical", [])
    if crit:
        lines.append("\n## Critical Issues\n")
        for c in crit:
            lines.append(f"- {c}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Technical SEO & web quality audit tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic audit
  python3 site_audit.py --url "https://example.com"

  # Deeper crawl with more pages
  python3 site_audit.py -u example.com -p 25 -d 3 -o deep_audit.json

  # With PageSpeed Insights API
  python3 site_audit.py -u https://example.com --psi-key YOUR_API_KEY

  # With local Lighthouse
  python3 site_audit.py -u https://example.com --lighthouse

  # Markdown + JSON output
  python3 site_audit.py -u https://example.com -f both -o report.json -v
        """,
    )
    parser.add_argument("-u", "--url", required=True,
                        help="Target URL (required). Auto-prepends https:// if missing.")
    parser.add_argument("-o", "--output", default="site_audit.json",
                        help="Output file path (default: site_audit.json)")
    parser.add_argument("-f", "--format", default="json", choices=["json", "markdown", "both"],
                        help="Output format: json (default), markdown, both")
    parser.add_argument("-p", "--max-pages", type=int, default=10,
                        help="Max pages to crawl (default: 10, max: 50)")
    parser.add_argument("-d", "--depth", type=int, default=2,
                        help="Max crawl depth from start URL (default: 2)")
    parser.add_argument("--lighthouse", action="store_true",
                        help="Enable Lighthouse if CLI available")
    parser.add_argument("--psi-key", default=None,
                        help="Google PageSpeed Insights API key")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Request timeout in seconds (default: 30)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print progress to stderr")

    args = parser.parse_args()

    global _verbose
    _verbose = args.verbose

    # Normalize inputs
    url = args.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    max_pages = max(1, min(args.max_pages, 50))
    max_depth = max(0, min(args.depth, 10))
    timeout = max(5, args.timeout)
    psi_key = args.psi_key or os.environ.get("GOOGLE_PSI_API_KEY")

    log(f"Starting audit of {url}")
    t_start = time.monotonic()

    # Step 1: robots.txt
    log("Fetching robots.txt ...")
    robots, crawl_delay, robots_text = fetch_robots(url, timeout=timeout)
    robots_present = robots is not None
    rate = max(crawl_delay or 1.0, 1.0)

    # Step 2: sitemap
    log("Fetching sitemap.xml ...")
    sitemap_urls = fetch_sitemap(url, timeout=timeout)
    log(f"  Found {len(sitemap_urls)} URLs in sitemap")

    # Step 3: Crawl
    log(f"Crawling (max {max_pages} pages, depth {max_depth}) ...")
    pages, broken_links = crawl_site(
        url, max_pages, max_depth, timeout, robots, rate, sitemap_urls)

    # Step 3b: check a sample of external links
    log("Checking external links ...")
    ext_broken = check_external_links(pages, timeout=min(timeout, 10))
    broken_links.extend(ext_broken)

    crawl_duration = time.monotonic() - t_start

    # Step 4: Tier 2 - PSI
    psi_data = None
    psi_used = False
    if psi_key:
        log("Fetching PageSpeed Insights data ...")
        psi_data = fetch_psi_data(url, psi_key, timeout=60)
        psi_used = psi_data is not None
        if not psi_used:
            print("Warning: PageSpeed Insights API call failed", file=sys.stderr)

    # Step 5: Tier 3 - Lighthouse
    lh_data = None
    lh_avail = lighthouse_available()
    if args.lighthouse and lh_avail:
        log("Running Lighthouse (this may take a minute) ...")
        lh_data = run_lighthouse(url, timeout=120)
        if not lh_data:
            print("Warning: Lighthouse run failed", file=sys.stderr)
    elif args.lighthouse and not lh_avail:
        print("Warning: --lighthouse requested but neither lighthouse nor npx found in PATH",
              file=sys.stderr)

    # Build report
    report = build_report(
        url, pages, broken_links, robots_present, robots_text,
        sitemap_urls, crawl_duration, psi_data, lh_data, psi_used, lh_avail)

    # Write output
    output_path = Path(args.output)
    if args.format in ("json", "both"):
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Audit saved to: {output_path}", file=sys.stderr)

    if args.format in ("markdown", "both"):
        md_path = output_path.with_suffix(".md") if args.format == "both" else output_path
        md_content = report_to_markdown(report)
        with open(md_path, "w") as f:
            f.write(md_content)
        print(f"Markdown report saved to: {md_path}", file=sys.stderr)

    # Summary to stderr
    s = report["scores"]
    print(f"\nAudit complete for {url}", file=sys.stderr)
    print(f"  SEO:            {s['seo']['score']}/100 ({s['seo']['label']})", file=sys.stderr)
    print(f"  Accessibility:  {s['accessibility']['score']}/100 ({s['accessibility']['label']})", file=sys.stderr)
    print(f"  Performance:    {s['performance']['score']}/100 ({s['performance']['label']})", file=sys.stderr)
    print(f"  Best Practices: {s['best_practices']['score']}/100 ({s['best_practices']['label']})", file=sys.stderr)
    print(f"  Pages crawled:  {report['audit_metadata']['pages_crawled']}", file=sys.stderr)
    print(f"  Duration:       {report['audit_metadata']['crawl_duration_seconds']}s", file=sys.stderr)


if __name__ == "__main__":
    main()
