#!/usr/bin/env python3
"""
Positioning Matrix Generator (2x2)
Generates competitive positioning matrices for market analysis.

Usage:
  python positioning_matrix.py --companies '["You", "Comp A", "Comp B"]' \
    --x-values '[70, 90, 30]' --y-values '[80, 85, 40]' --output matrix.png
"""

import argparse
import json
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    print("Error: matplotlib not installed. Run: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def create_positioning_matrix(
    companies: list,
    x_values: list,
    y_values: list,
    x_label: str = "X Axis",
    y_label: str = "Y Axis",
    title: str = "Competitive Positioning",
    quadrant_labels: list = None,
    highlight: int = None,
    sizes: list = None,
    colors: list = None,
    width: float = 10,
    height: float = 10,
    dpi: int = 150,
    output: str = "positioning_matrix.png"
):
    """Generate a 2x2 positioning matrix and save to file."""
    
    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    
    # Default colors
    if colors is None:
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', 
                  '#00BCD4', '#795548', '#607D8B']
    
    # Extend colors
    while len(colors) < len(companies):
        colors = colors + colors
    
    # Highlight first company (usually "you")
    if highlight is not None:
        colors[highlight] = '#4CAF50'  # Green for highlighted
    
    # Default sizes
    if sizes is None:
        sizes = [300] * len(companies)
    else:
        # Normalize sizes
        max_size = max(sizes)
        sizes = [s / max_size * 500 + 100 for s in sizes]
    
    # Plot points
    for i, (company, x, y) in enumerate(zip(companies, x_values, y_values)):
        color = colors[i]
        size = sizes[i]
        edge_color = '#333333' if highlight is not None and i == highlight else 'white'
        edge_width = 3 if highlight is not None and i == highlight else 1
        
        ax.scatter(x, y, s=size, c=color, edgecolors=edge_color, 
                  linewidths=edge_width, alpha=0.8, zorder=5)
        
        # Label
        ax.annotate(company, (x, y), textcoords="offset points", 
                   xytext=(0, 12), ha='center', fontsize=11, fontweight='bold')
    
    # Set axis limits
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    # Draw quadrant lines
    ax.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(x=50, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    
    # Quadrant labels
    if quadrant_labels and len(quadrant_labels) >= 4:
        # [top-left, top-right, bottom-left, bottom-right]
        ax.text(25, 75, quadrant_labels[0], ha='center', va='center', 
               fontsize=12, alpha=0.4, fontweight='bold')
        ax.text(75, 75, quadrant_labels[1], ha='center', va='center', 
               fontsize=12, alpha=0.4, fontweight='bold')
        ax.text(25, 25, quadrant_labels[2], ha='center', va='center', 
               fontsize=12, alpha=0.4, fontweight='bold')
        ax.text(75, 25, quadrant_labels[3], ha='center', va='center', 
               fontsize=12, alpha=0.4, fontweight='bold')
    
    # Labels and title
    ax.set_xlabel(x_label, fontsize=12, fontweight='bold')
    ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Style
    ax.set_facecolor('#f8f9fa')
    ax.grid(True, alpha=0.3)
    
    # Add arrows to show direction
    ax.annotate('', xy=(100, 0), xytext=(0, 0),
               arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
    ax.annotate('', xy=(0, 100), xytext=(0, 0),
               arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))
    
    plt.tight_layout()
    plt.savefig(output, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate 2x2 positioning matrices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic positioning matrix
  python positioning_matrix.py \\
    --companies '["Your Product", "Salesforce", "HubSpot", "Pipedrive"]' \\
    --x-values '[50, 90, 70, 30]' \\
    --y-values '[75, 95, 60, 40]' \\
    --x-label "Price (Low → High)" \\
    --y-label "Features (Basic → Advanced)"
  
  # With quadrant labels and highlight
  python positioning_matrix.py \\
    --companies '["You", "Comp A", "Comp B"]' \\
    --x-values '[60, 80, 35]' \\
    --y-values '[80, 70, 50]' \\
    --quadrant-labels '["Niche Premium", "Market Leaders", "Budget Basic", "Feature-lite"]' \\
    --highlight 0
        """
    )
    
    parser.add_argument("--companies", required=True, help="JSON array of company names")
    parser.add_argument("--x-values", required=True, help="JSON array of x-axis values (0-100)")
    parser.add_argument("--y-values", required=True, help="JSON array of y-axis values (0-100)")
    parser.add_argument("--x-label", default="X Axis", help="X-axis label")
    parser.add_argument("--y-label", default="Y Axis", help="Y-axis label")
    parser.add_argument("--title", default="Competitive Positioning", help="Chart title")
    parser.add_argument("--quadrant-labels", help="JSON array of 4 quadrant labels [TL, TR, BL, BR]")
    parser.add_argument("--highlight", type=int, help="Index of company to highlight")
    parser.add_argument("--sizes", help="JSON array of bubble sizes (for market share)")
    parser.add_argument("--colors", help="JSON array of colors")
    parser.add_argument("--width", type=float, default=10, help="Width in inches")
    parser.add_argument("--height", type=float, default=10, help="Height in inches")
    parser.add_argument("--dpi", type=int, default=150, help="Resolution")
    parser.add_argument("--output", "-o", default="positioning_matrix.png", help="Output file")
    
    args = parser.parse_args()
    
    try:
        companies = json.loads(args.companies)
        x_values = json.loads(args.x_values)
        y_values = json.loads(args.y_values)
        quadrant_labels = json.loads(args.quadrant_labels) if args.quadrant_labels else None
        sizes = json.loads(args.sizes) if args.sizes else None
        colors = json.loads(args.colors) if args.colors else None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not (len(companies) == len(x_values) == len(y_values)):
        print("Error: companies, x-values, and y-values must have same length", file=sys.stderr)
        sys.exit(1)
    
    output = create_positioning_matrix(
        companies=companies,
        x_values=x_values,
        y_values=y_values,
        x_label=args.x_label,
        y_label=args.y_label,
        title=args.title,
        quadrant_labels=quadrant_labels,
        highlight=args.highlight,
        sizes=sizes,
        colors=colors,
        width=args.width,
        height=args.height,
        dpi=args.dpi,
        output=args.output
    )
    
    print(f"✅ Positioning matrix saved: {output}")


if __name__ == "__main__":
    main()
