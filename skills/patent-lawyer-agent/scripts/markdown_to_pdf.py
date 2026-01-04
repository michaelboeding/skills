#!/usr/bin/env python3
"""
Convert patent application Markdown to PDF with embedded images.

Usage:
    python3 markdown_to_pdf.py --input patent_application.md --output patent_application.pdf

Requires: pip install markdown weasyprint
"""

import argparse
import os
import sys
import base64
import re
from pathlib import Path

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
        print(f"Error: Missing required packages: {', '.join(missing)}", file=sys.stderr)
        print(f"Install with: pip install {' '.join(missing)}", file=sys.stderr)
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
            # Read and encode image
            with open(full_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Determine mime type
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
            return match.group(0)  # Return original if not found
    
    # Match ![alt](path) pattern
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    return re.sub(pattern, replace_image, markdown_content)

def markdown_to_pdf(input_path: str, output_path: str, title: str = "Patent Application"):
    """Convert Markdown file to PDF with embedded images."""
    
    import markdown
    from weasyprint import HTML, CSS
    
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Read markdown content
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Embed images as base64
    md_content = embed_images_as_base64(md_content, input_file.parent)
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    html_body = md.convert(md_content)
    
    # Patent-specific CSS
    css = CSS(string='''
        @page {
            size: letter;
            margin: 1in;
            @top-center {
                content: "Patent Application";
                font-size: 9pt;
                color: #666;
            }
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }
        }
        
        body {
            font-family: "Times New Roman", Times, serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #000;
        }
        
        h1 {
            font-size: 16pt;
            font-weight: bold;
            text-align: center;
            margin-top: 24pt;
            margin-bottom: 12pt;
            page-break-after: avoid;
        }
        
        h2 {
            font-size: 14pt;
            font-weight: bold;
            margin-top: 18pt;
            margin-bottom: 10pt;
            text-transform: uppercase;
            page-break-after: avoid;
        }
        
        h3 {
            font-size: 12pt;
            font-weight: bold;
            margin-top: 14pt;
            margin-bottom: 8pt;
            page-break-after: avoid;
        }
        
        p {
            text-align: justify;
            margin-bottom: 10pt;
            text-indent: 0.5in;
        }
        
        p:first-of-type {
            text-indent: 0;
        }
        
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20pt auto;
            border: 1px solid #ccc;
        }
        
        /* Figure captions */
        img + em, img + p > em:first-child {
            display: block;
            text-align: center;
            font-style: italic;
            font-size: 10pt;
            margin-top: 8pt;
            margin-bottom: 16pt;
        }
        
        /* Claims formatting */
        ol {
            margin-left: 0.5in;
            padding-left: 0;
        }
        
        ol li {
            margin-bottom: 12pt;
            text-align: justify;
        }
        
        /* Code blocks for claim structure */
        pre, code {
            font-family: "Courier New", monospace;
            font-size: 10pt;
            background-color: #f5f5f5;
            padding: 2pt 4pt;
        }
        
        pre {
            padding: 10pt;
            margin: 10pt 0;
            white-space: pre-wrap;
            border: 1px solid #ddd;
        }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 12pt 0;
            font-size: 10pt;
        }
        
        th, td {
            border: 1px solid #000;
            padding: 6pt;
            text-align: left;
        }
        
        th {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        
        /* Disclaimer styling */
        blockquote, .disclaimer {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10pt;
            margin: 12pt 0;
            font-style: italic;
        }
        
        /* Horizontal rules */
        hr {
            border: none;
            border-top: 1px solid #000;
            margin: 18pt 0;
        }
        
        /* Page breaks */
        h1 {
            page-break-before: always;
        }
        
        h1:first-of-type {
            page-break-before: avoid;
        }
    ''')
    
    # Full HTML document
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    '''
    
    # Generate PDF
    HTML(string=html_content).write_pdf(output_file, stylesheets=[css])
    
    print(f"✓ PDF generated: {output_file}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")
    
    return str(output_file)

def main():
    parser = argparse.ArgumentParser(
        description='Convert patent application Markdown to PDF'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input Markdown file path'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output PDF file path (default: same name as input with .pdf)'
    )
    parser.add_argument(
        '--title', '-t',
        default='Patent Application',
        help='Document title for header'
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Default output path
    if not args.output:
        input_path = Path(args.input)
        args.output = str(input_path.with_suffix('.pdf'))
    
    # Convert
    markdown_to_pdf(args.input, args.output, args.title)

if __name__ == '__main__':
    main()
