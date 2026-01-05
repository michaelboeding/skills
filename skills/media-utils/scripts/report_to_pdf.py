#!/usr/bin/env python3
"""
Convert Markdown reports to professional PDF documents.

Usage:
    python3 report_to_pdf.py --input report.md --output report.pdf
    python3 report_to_pdf.py --input report.md --style executive --title "Market Analysis"

Styles:
    - business (default): Clean, professional look for business reports
    - executive: Executive summary style with larger fonts
    - technical: Technical documentation style
    - minimal: Minimal styling, maximum content

Requires: pip install markdown weasyprint
"""

import argparse
import os
import sys
import base64
import re
from pathlib import Path
from datetime import datetime


def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    
    try:
        import markdown
    except ImportError:
        missing.append("markdown")
    
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        missing.append("weasyprint")
    
    if missing:
        print(f"""
╭─────────────────────────────────────────────────────────────────╮
│  Missing Dependencies: {', '.join(missing):<39} │
╰─────────────────────────────────────────────────────────────────╯

To install all skill dependencies, run:

   ./scripts/install.sh
   
Or: pip install -r requirements.txt
Or: pip install {' '.join(missing)}
""", file=sys.stderr)
        return False
    return True


def embed_images_as_base64(markdown_content: str, base_path: Path) -> str:
    """Replace image paths with base64 embedded data."""
    
    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # Handle relative paths
        if not os.path.isabs(image_path):
            full_path = base_path / image_path
        else:
            full_path = Path(image_path)
        
        if full_path.exists():
            with open(full_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            suffix = full_path.suffix.lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(suffix, 'image/png')
            
            return f'![{alt_text}](data:{mime_type};base64,{image_data})'
        else:
            print(f"Warning: Image not found: {full_path}", file=sys.stderr)
            return match.group(0)
    
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    return re.sub(pattern, replace_image, markdown_content)


def get_style_css(style: str, title: str) -> str:
    """Get CSS for the specified style."""
    
    base_css = '''
        @page {
            size: letter;
            margin: 0.75in;
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }
        }
        
        * {
            box-sizing: border-box;
        }
        
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 16pt auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 12pt 0;
            font-size: 10pt;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8pt;
            text-align: left;
        }
        
        th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        
        tr:nth-child(even) {
            background-color: #fafafa;
        }
        
        pre, code {
            font-family: "SF Mono", Consolas, monospace;
            font-size: 9pt;
            background-color: #f5f5f5;
            padding: 2pt 4pt;
            border-radius: 3pt;
        }
        
        pre {
            padding: 12pt;
            margin: 12pt 0;
            overflow-x: auto;
            border: 1px solid #e0e0e0;
        }
        
        blockquote {
            border-left: 4px solid #3b82f6;
            margin: 12pt 0;
            padding: 12pt 16pt;
            background-color: #eff6ff;
            font-style: italic;
        }
        
        hr {
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 24pt 0;
        }
        
        ul, ol {
            margin: 8pt 0;
            padding-left: 24pt;
        }
        
        li {
            margin-bottom: 4pt;
        }
    '''
    
    styles = {
        'business': '''
            body {
                font-family: "Helvetica Neue", Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.5;
                color: #333;
            }
            
            h1 {
                font-size: 24pt;
                font-weight: 600;
                color: #1a1a1a;
                margin-top: 0;
                margin-bottom: 8pt;
                border-bottom: 2px solid #3b82f6;
                padding-bottom: 8pt;
            }
            
            h2 {
                font-size: 16pt;
                font-weight: 600;
                color: #1a1a1a;
                margin-top: 24pt;
                margin-bottom: 12pt;
                page-break-after: avoid;
            }
            
            h3 {
                font-size: 13pt;
                font-weight: 600;
                color: #333;
                margin-top: 18pt;
                margin-bottom: 8pt;
            }
            
            h4 {
                font-size: 11pt;
                font-weight: 600;
                color: #555;
                margin-top: 14pt;
                margin-bottom: 6pt;
            }
            
            p {
                margin-bottom: 10pt;
            }
            
            th {
                background-color: #3b82f6;
                color: white;
            }
        ''',
        
        'executive': '''
            body {
                font-family: Georgia, "Times New Roman", serif;
                font-size: 12pt;
                line-height: 1.6;
                color: #222;
            }
            
            h1 {
                font-size: 28pt;
                font-weight: normal;
                color: #1a1a1a;
                margin-top: 0;
                margin-bottom: 16pt;
                text-align: center;
                border-bottom: 3px double #333;
                padding-bottom: 16pt;
            }
            
            h2 {
                font-size: 18pt;
                font-weight: normal;
                color: #1a1a1a;
                margin-top: 28pt;
                margin-bottom: 14pt;
                border-bottom: 1px solid #ccc;
                padding-bottom: 6pt;
            }
            
            h3 {
                font-size: 14pt;
                font-weight: bold;
                color: #333;
                margin-top: 20pt;
                margin-bottom: 10pt;
            }
            
            p {
                margin-bottom: 12pt;
                text-align: justify;
            }
            
            th {
                background-color: #2c3e50;
                color: white;
            }
            
            blockquote {
                border-left-color: #2c3e50;
                background-color: #f8f9fa;
            }
        ''',
        
        'technical': '''
            body {
                font-family: "SF Pro Text", -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 10pt;
                line-height: 1.4;
                color: #333;
            }
            
            h1 {
                font-size: 20pt;
                font-weight: 700;
                color: #000;
                margin-top: 0;
                margin-bottom: 12pt;
                background-color: #f0f0f0;
                padding: 12pt;
                margin-left: -12pt;
                margin-right: -12pt;
            }
            
            h2 {
                font-size: 14pt;
                font-weight: 700;
                color: #000;
                margin-top: 20pt;
                margin-bottom: 10pt;
                border-bottom: 2px solid #000;
                padding-bottom: 4pt;
            }
            
            h3 {
                font-size: 12pt;
                font-weight: 600;
                color: #333;
                margin-top: 16pt;
                margin-bottom: 8pt;
            }
            
            p {
                margin-bottom: 8pt;
            }
            
            th {
                background-color: #333;
                color: white;
            }
            
            code {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            
            pre {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
            }
        ''',
        
        'minimal': '''
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 11pt;
                line-height: 1.5;
                color: #000;
            }
            
            h1 {
                font-size: 20pt;
                font-weight: 600;
                margin-top: 0;
                margin-bottom: 12pt;
            }
            
            h2 {
                font-size: 16pt;
                font-weight: 600;
                margin-top: 20pt;
                margin-bottom: 10pt;
            }
            
            h3 {
                font-size: 13pt;
                font-weight: 600;
                margin-top: 16pt;
                margin-bottom: 8pt;
            }
            
            p {
                margin-bottom: 10pt;
            }
        '''
    }
    
    return base_css + styles.get(style, styles['business'])


def markdown_to_pdf(input_path: str, output_path: str, title: str = None, 
                    style: str = "business", include_toc: bool = False) -> str:
    """Convert Markdown file to PDF.
    
    Args:
        input_path: Path to input Markdown file
        output_path: Path to output PDF file
        title: Document title (extracted from H1 if not provided)
        style: CSS style theme (business, executive, technical, minimal)
        include_toc: Whether to include table of contents
    
    Returns:
        Path to generated PDF file
    """
    import markdown
    from weasyprint import HTML, CSS
    
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Read markdown content
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract title from first H1 if not provided
    if not title:
        h1_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        title = h1_match.group(1) if h1_match else "Report"
    
    # Embed images as base64
    md_content = embed_images_as_base64(md_content, input_file.parent)
    
    # Convert markdown to HTML
    extensions = ['tables', 'fenced_code', 'toc', 'nl2br']
    md = markdown.Markdown(extensions=extensions)
    html_body = md.convert(md_content)
    
    # Add TOC if requested
    toc_html = ""
    if include_toc and hasattr(md, 'toc'):
        toc_html = f'<div class="toc"><h2>Table of Contents</h2>{md.toc}</div>'
    
    # Get CSS
    css_content = get_style_css(style, title)
    css = CSS(string=css_content)
    
    # Add generated date
    generated_date = datetime.now().strftime("%B %d, %Y")
    
    # Full HTML document
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
    </head>
    <body>
        {toc_html}
        {html_body}
        <footer style="margin-top: 40pt; padding-top: 12pt; border-top: 1px solid #e0e0e0; font-size: 9pt; color: #666;">
            Generated on {generated_date}
        </footer>
    </body>
    </html>
    '''
    
    # Generate PDF
    HTML(string=html_content).write_pdf(output_file, stylesheets=[css])
    
    print(f"✓ PDF generated: {output_file}")
    print(f"  Style: {style}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")
    
    return str(output_file)


def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown reports to professional PDF documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Styles:
  business   Clean, professional look (default)
  executive  Executive summary style with larger fonts
  technical  Technical documentation style
  minimal    Minimal styling, maximum content

Examples:
  # Basic conversion
  python report_to_pdf.py -i analysis.md -o analysis.pdf
  
  # With custom title and executive style
  python report_to_pdf.py -i report.md -o report.pdf --title "Q4 Market Analysis" --style executive
  
  # Technical documentation
  python report_to_pdf.py -i docs.md -o docs.pdf --style technical --toc
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                        help='Input Markdown file path')
    parser.add_argument('--output', '-o',
                        help='Output PDF file path (default: same name as input with .pdf)')
    parser.add_argument('--title', '-t',
                        help='Document title (default: extracted from first H1)')
    parser.add_argument('--style', '-s', default='business',
                        choices=['business', 'executive', 'technical', 'minimal'],
                        help='PDF style theme (default: business)')
    parser.add_argument('--toc', action='store_true',
                        help='Include table of contents')
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Default output path
    if not args.output:
        input_path = Path(args.input)
        args.output = str(input_path.with_suffix('.pdf'))
    
    # Convert
    markdown_to_pdf(args.input, args.output, args.title, args.style, args.toc)


if __name__ == '__main__':
    main()
