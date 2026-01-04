#!/usr/bin/env python3
"""
Comparison Table Generator
Generates feature comparison tables as images.

Usage:
  python comparison_table.py --features '["Feature A", "Feature B"]' \
    --companies '["You", "Comp A"]' --data '[["✓", "✗"], ["✓", "✓"]]' --output table.png
"""

import argparse
import json
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    print("""
╭─────────────────────────────────────────────────────────────────╮
│  Missing Dependency: matplotlib                                 │
╰─────────────────────────────────────────────────────────────────╯

To install all skill dependencies, run:

   ./scripts/install.sh
   
Or: pip install -r requirements.txt
Or: pip install matplotlib
""", file=sys.stderr)
    sys.exit(1)


def create_comparison_table(
    features: list,
    companies: list,
    data: list,
    title: str = "Feature Comparison",
    highlight_column: int = None,
    use_colors: bool = False,
    width: float = 10,
    height: float = None,
    dpi: int = 150,
    output: str = "comparison_table.png"
):
    """Generate a comparison table as an image."""
    
    # Auto-calculate height based on rows
    if height is None:
        height = max(4, len(features) * 0.6 + 2)
    
    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    ax.axis('off')
    
    # Prepare table data
    cell_text = []
    for i, feature in enumerate(features):
        row = [feature] + data[i]
        cell_text.append(row)
    
    # Column headers
    columns = ["Feature"] + companies
    
    # Create table
    table = ax.table(
        cellText=cell_text,
        colLabels=columns,
        loc='center',
        cellLoc='center'
    )
    
    # Style table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)
    
    # Color cells
    for i in range(len(cell_text) + 1):  # +1 for header
        for j in range(len(columns)):
            cell = table[(i, j)]
            
            # Header row
            if i == 0:
                cell.set_facecolor('#2196F3')
                cell.set_text_props(color='white', fontweight='bold')
                if highlight_column is not None and j == highlight_column + 1:
                    cell.set_facecolor('#4CAF50')
            else:
                # Data rows
                if j == 0:
                    # Feature column
                    cell.set_facecolor('#f5f5f5')
                    cell.set_text_props(fontweight='bold')
                else:
                    # Data cells
                    text = cell_text[i-1][j]
                    if highlight_column is not None and j == highlight_column + 1:
                        cell.set_facecolor('#e8f5e9')
                    
                    if use_colors:
                        if text in ['✓', '✅', 'Yes', 'yes', 'Y', 'Full', 'true', 'True']:
                            cell.set_facecolor('#c8e6c9')
                        elif text in ['✗', '❌', 'No', 'no', 'N', 'None', 'false', 'False']:
                            cell.set_facecolor('#ffcdd2')
                        elif text in ['⚠️', 'Partial', 'partial', 'Limited', 'limited']:
                            cell.set_facecolor('#fff9c4')
            
            cell.set_edgecolor('#e0e0e0')
    
    # Title
    if title:
        plt.title(title, fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate comparison tables as images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple comparison
  python comparison_table.py \\
    --features '["SSO", "API Access", "Analytics", "Support"]' \\
    --companies '["You", "Competitor A", "Competitor B"]' \\
    --data '[["✓", "✓", "✗"], ["✓", "✗", "✓"], ["✓", "✓", "✓"], ["24/7", "Email", "Chat"]]'
  
  # With highlighting and colors
  python comparison_table.py \\
    --features '["Feature 1", "Feature 2", "Feature 3"]' \\
    --companies '["Your Product", "Comp A", "Comp B"]' \\
    --data '[["✓", "✗", "✓"], ["✓", "✓", "✗"], ["✓", "✗", "✗"]]' \\
    --highlight-column 0 --use-colors
        """
    )
    
    parser.add_argument("--features", required=True, help="JSON array of feature names")
    parser.add_argument("--companies", required=True, help="JSON array of company names")
    parser.add_argument("--data", required=True, help="JSON 2D array: [[row1 values], [row2 values], ...]")
    parser.add_argument("--title", default="Feature Comparison", help="Table title")
    parser.add_argument("--highlight-column", type=int, help="Index of column to highlight (0 = first company)")
    parser.add_argument("--use-colors", action="store_true", help="Color cells based on values")
    parser.add_argument("--width", type=float, default=10, help="Width in inches")
    parser.add_argument("--height", type=float, help="Height in inches (auto if not specified)")
    parser.add_argument("--dpi", type=int, default=150, help="Resolution")
    parser.add_argument("--output", "-o", default="comparison_table.png", help="Output file")
    
    args = parser.parse_args()
    
    try:
        features = json.loads(args.features)
        companies = json.loads(args.companies)
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    if len(features) != len(data):
        print("Error: features and data rows must have same length", file=sys.stderr)
        sys.exit(1)
    
    for i, row in enumerate(data):
        if len(row) != len(companies):
            print(f"Error: data row {i} has {len(row)} values but {len(companies)} companies", file=sys.stderr)
            sys.exit(1)
    
    output = create_comparison_table(
        features=features,
        companies=companies,
        data=data,
        title=args.title,
        highlight_column=args.highlight_column,
        use_colors=args.use_colors,
        width=args.width,
        height=args.height,
        dpi=args.dpi,
        output=args.output
    )
    
    print(f"✅ Comparison table saved: {output}")


if __name__ == "__main__":
    main()
