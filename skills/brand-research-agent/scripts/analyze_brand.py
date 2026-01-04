#!/usr/bin/env python3
"""
Brand Research - Website Analysis Script

This script helps capture brand elements from a website.
It can be used standalone or as part of the brand-research skill.

Usage:
  python analyze_brand.py --url "https://example.com" --output brand_profile.json
  python analyze_brand.py --url "https://example.com" --pages "about,products,pricing"
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser


class BrandDataExtractor(HTMLParser):
    """Extract brand-relevant data from HTML."""
    
    def __init__(self):
        super().__init__()
        self.colors = set()
        self.fonts = set()
        self.headings = []
        self.paragraphs = []
        self.links = []
        self.images = []
        self.meta = {}
        self.current_tag = None
        self.current_text = []
        self.in_style = False
        self.style_content = []
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)
        
        if tag == 'style':
            self.in_style = True
            
        if tag == 'meta':
            name = attrs_dict.get('name', attrs_dict.get('property', ''))
            content = attrs_dict.get('content', '')
            if name and content:
                self.meta[name] = content
                
        if tag == 'link' and attrs_dict.get('rel') == 'icon':
            self.images.append({
                'type': 'favicon',
                'src': attrs_dict.get('href', '')
            })
            
        if tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', '')
            if src:
                self.images.append({
                    'type': 'image',
                    'src': src,
                    'alt': alt
                })
                
        if tag == 'a':
            href = attrs_dict.get('href', '')
            self.links.append(href)
            
        # Extract inline styles for colors
        style = attrs_dict.get('style', '')
        if style:
            self._extract_colors_from_css(style)
            
    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False
            css = ''.join(self.style_content)
            self._extract_colors_from_css(css)
            self._extract_fonts_from_css(css)
            self.style_content = []
            
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            text = ''.join(self.current_text).strip()
            if text:
                self.headings.append({
                    'level': tag,
                    'text': text
                })
            self.current_text = []
            
        if tag == 'p':
            text = ''.join(self.current_text).strip()
            if text and len(text) > 20:  # Only meaningful paragraphs
                self.paragraphs.append(text)
            self.current_text = []
            
        self.current_tag = None
        
    def handle_data(self, data):
        if self.in_style:
            self.style_content.append(data)
        elif self.current_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
            self.current_text.append(data)
            
    def _extract_colors_from_css(self, css):
        """Extract hex colors from CSS."""
        # Hex colors
        hex_pattern = r'#[0-9A-Fa-f]{3,8}\b'
        for match in re.findall(hex_pattern, css):
            if len(match) in [4, 7, 9]:  # #RGB, #RRGGBB, #RRGGBBAA
                self.colors.add(match.upper())
                
        # RGB/RGBA colors
        rgb_pattern = r'rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)'
        for match in re.findall(rgb_pattern, css):
            r, g, b = int(match[0]), int(match[1]), int(match[2])
            hex_color = f'#{r:02X}{g:02X}{b:02X}'
            self.colors.add(hex_color)
            
    def _extract_fonts_from_css(self, css):
        """Extract font families from CSS."""
        font_pattern = r'font-family\s*:\s*([^;]+)'
        for match in re.findall(font_pattern, css):
            # Clean up font family string
            fonts = match.strip().strip('"').strip("'")
            self.fonts.add(fonts)


def fetch_page(url: str) -> str:
    """Fetch a web page and return its HTML content."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    request = Request(url, headers=headers)
    
    try:
        with urlopen(request, timeout=30) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return ""


def find_pages(html: str, base_url: str) -> dict:
    """Find common pages (about, products, pricing, etc.)."""
    pages = {
        'about': None,
        'products': None,
        'services': None,
        'pricing': None,
        'features': None,
        'contact': None,
        'blog': None
    }
    
    # Common URL patterns
    patterns = {
        'about': ['/about', '/about-us', '/company', '/our-story'],
        'products': ['/products', '/solutions', '/offerings'],
        'services': ['/services'],
        'pricing': ['/pricing', '/plans', '/packages'],
        'features': ['/features', '/capabilities'],
        'contact': ['/contact', '/contact-us'],
        'blog': ['/blog', '/news', '/resources', '/insights']
    }
    
    # Find links in HTML
    link_pattern = r'href=["\']([^"\']+)["\']'
    links = re.findall(link_pattern, html.lower())
    
    for page_type, url_patterns in patterns.items():
        for link in links:
            for pattern in url_patterns:
                if pattern in link:
                    # Construct full URL
                    if link.startswith('http'):
                        pages[page_type] = link
                    else:
                        pages[page_type] = urljoin(base_url, link)
                    break
            if pages[page_type]:
                break
                
    return pages


def analyze_website(url: str, extra_pages: list = None) -> dict:
    """Analyze a website and extract brand data."""
    
    print(f"🔍 Analyzing: {url}")
    
    # Parse base URL
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # Fetch homepage
    homepage_html = fetch_page(url)
    if not homepage_html:
        return {"error": f"Could not fetch {url}"}
    
    # Extract data from homepage
    extractor = BrandDataExtractor()
    extractor.feed(homepage_html)
    
    # Find other pages
    discovered_pages = find_pages(homepage_html, base_url)
    
    # Fetch and analyze additional pages
    all_headings = list(extractor.headings)
    all_paragraphs = list(extractor.paragraphs)
    all_images = list(extractor.images)
    
    pages_analyzed = [url]
    
    # Add user-specified pages
    if extra_pages:
        for page in extra_pages:
            if not page.startswith('http'):
                page = urljoin(base_url, '/' + page.strip('/'))
            discovered_pages[page] = page
    
    # Analyze discovered pages
    for page_type, page_url in discovered_pages.items():
        if page_url and page_url not in pages_analyzed:
            print(f"  📄 Analyzing: {page_type} - {page_url}")
            html = fetch_page(page_url)
            if html:
                page_extractor = BrandDataExtractor()
                page_extractor.feed(html)
                all_headings.extend(page_extractor.headings)
                all_paragraphs.extend(page_extractor.paragraphs)
                all_images.extend(page_extractor.images)
                extractor.colors.update(page_extractor.colors)
                extractor.fonts.update(page_extractor.fonts)
                pages_analyzed.append(page_url)
    
    # Build raw data output
    raw_data = {
        "website": url,
        "analyzed_date": datetime.now().isoformat(),
        "pages_analyzed": pages_analyzed,
        "meta": extractor.meta,
        "colors_found": sorted(list(extractor.colors)),
        "fonts_found": sorted(list(extractor.fonts)),
        "headings": all_headings[:50],  # Limit to first 50
        "sample_paragraphs": all_paragraphs[:20],  # Limit to first 20
        "images": all_images[:30],  # Limit to first 30
    }
    
    return raw_data


def create_brand_profile_template(raw_data: dict) -> dict:
    """Create a brand profile template from raw data."""
    
    # Try to extract brand name from meta or title
    brand_name = raw_data.get("meta", {}).get("og:site_name", "")
    if not brand_name:
        brand_name = raw_data.get("meta", {}).get("og:title", "").split(" - ")[0]
    if not brand_name:
        # Extract from URL
        parsed = urlparse(raw_data.get("website", ""))
        brand_name = parsed.netloc.replace("www.", "").split(".")[0].title()
    
    # Get tagline from meta description or first h1
    tagline = raw_data.get("meta", {}).get("description", "")
    if not tagline and raw_data.get("headings"):
        h1s = [h for h in raw_data["headings"] if h["level"] == "h1"]
        if h1s:
            tagline = h1s[0]["text"]
    
    # Organize colors (most common first)
    colors = raw_data.get("colors_found", [])
    
    profile = {
        "brand": {
            "name": brand_name,
            "website": raw_data.get("website", ""),
            "tagline": tagline[:200] if tagline else "",
            "analyzed_date": raw_data.get("analyzed_date", "")
        },
        "visual": {
            "colors": {
                "found": colors[:10],
                "primary": colors[0] if colors else "#000000",
                "secondary": colors[1] if len(colors) > 1 else "#FFFFFF",
                "accent": colors[2] if len(colors) > 2 else "#0066CC",
                "notes": "Review and adjust based on visual analysis"
            },
            "typography": {
                "found": list(raw_data.get("fonts_found", [])),
                "headings": "Needs analysis",
                "body": "Needs analysis"
            },
            "imagery_style": {
                "notes": "Analyze screenshots for imagery style"
            }
        },
        "voice": {
            "sample_headlines": [h["text"] for h in raw_data.get("headings", [])[:10]],
            "sample_copy": raw_data.get("sample_paragraphs", [])[:5],
            "tone": ["Needs analysis"],
            "notes": "Analyze copy samples for voice patterns"
        },
        "products": {
            "notes": "Extract from product pages",
            "inferred_category": raw_data.get("meta", {}).get("og:type", "website")
        },
        "audience": {
            "notes": "Infer from messaging and content"
        },
        "positioning": {
            "notes": "Analyze competitive claims and messaging"
        },
        "content_guidelines": {
            "for_video_producer": {
                "music_style": "Based on brand personality",
                "voiceover_tone": "Based on voice analysis",
                "visual_style": "Based on visual analysis"
            },
            "for_audio_producer": {
                "voiceover_direction": "Based on voice analysis",
                "music_mood": "Based on brand personality"
            }
        },
        "_raw_data": {
            "pages_analyzed": raw_data.get("pages_analyzed", []),
            "all_colors": raw_data.get("colors_found", []),
            "all_fonts": raw_data.get("fonts_found", []),
            "meta_tags": raw_data.get("meta", {})
        }
    }
    
    return profile


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a brand's website and extract brand elements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python analyze_brand.py --url "https://example.com"
  
  # With specific pages
  python analyze_brand.py --url "https://example.com" --pages "about,products,pricing"
  
  # Save to specific file
  python analyze_brand.py --url "https://example.com" -o my_brand.json
  
  # Raw data only (for further processing)
  python analyze_brand.py --url "https://example.com" --raw-only

Output:
  The script produces a brand_profile.json with:
  - Discovered colors and fonts
  - Sample headlines and copy
  - Meta information
  - Template sections for agent analysis
  
  Use this as input for the 5 brand analysis agents to complete
  the full brand profile.
        """
    )
    
    parser.add_argument("--url", "-u", required=True,
                        help="Website URL to analyze")
    parser.add_argument("--pages", "-p",
                        help="Comma-separated list of additional pages to analyze")
    parser.add_argument("--output", "-o", default="brand_profile.json",
                        help="Output file path (default: brand_profile.json)")
    parser.add_argument("--raw-only", action="store_true",
                        help="Output raw extracted data only")
    
    args = parser.parse_args()
    
    # Parse extra pages
    extra_pages = []
    if args.pages:
        extra_pages = [p.strip() for p in args.pages.split(",")]
    
    # Ensure URL has protocol
    url = args.url
    if not url.startswith("http"):
        url = "https://" + url
    
    print("=" * 60)
    print("Brand Research - Website Analyzer")
    print("=" * 60)
    print()
    
    # Analyze website
    raw_data = analyze_website(url, extra_pages)
    
    if "error" in raw_data:
        print(f"\n❌ Error: {raw_data['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Create output
    if args.raw_only:
        output = raw_data
    else:
        output = create_brand_profile_template(raw_data)
    
    # Save to file
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print()
    print("=" * 60)
    print(f"✅ Brand profile saved to: {output_path}")
    print("=" * 60)
    print()
    print(f"Brand: {output.get('brand', {}).get('name', 'Unknown')}")
    print(f"Pages analyzed: {len(raw_data.get('pages_analyzed', []))}")
    print(f"Colors found: {len(raw_data.get('colors_found', []))}")
    print(f"Fonts found: {len(raw_data.get('fonts_found', []))}")
    print()
    print("Next steps:")
    print("1. Review the generated profile")
    print("2. Run the 5 brand analysis agents to complete the analysis")
    print("3. Use the profile with producer skills: --brand brand_profile.json")


if __name__ == "__main__":
    main()
