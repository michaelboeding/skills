#!/usr/bin/env python3
"""
Pie Chart Generator
Generates pie or donut charts for proportional data.

Usage:
  python pie_chart.py --labels '["A", "B", "C"]' --values '[40, 35, 25]' --output chart.png
"""

import argparse
import json
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    print("Error: matplotlib not installed. Run: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def create_pie_chart(
    labels: list,
    values: list,
    title: str = "",
    colors: list = None,
    donut: bool = False,
    explode_index: int = None,
    show_percent: bool = True,
    show_values: bool = False,
    width: float = 8,
    height: float = 8,
    dpi: int = 150,
    output: str = "pie_chart.png"
):
    """Generate a pie chart and save to file."""
    
    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    
    # Default colors
    if colors is None:
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', 
                  '#00BCD4', '#795548', '#607D8B', '#CDDC39', '#FF5722']
    
    # Extend colors if needed
    while len(colors) < len(labels):
        colors = colors + colors
    colors = colors[:len(labels)]
    
    # Explode effect
    explode = [0] * len(labels)
    if explode_index is not None and 0 <= explode_index < len(labels):
        explode[explode_index] = 0.1
    
    # Auto-format function
    def autopct_format(pct):
        if show_percent and show_values:
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f'{pct:.1f}%\n(${val:,})' if val > 0 else f'{pct:.1f}%'
        elif show_percent:
            return f'{pct:.1f}%'
        elif show_values:
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f'{val:,}'
        return ''
    
    # Create pie
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=colors,
        explode=explode,
        autopct=autopct_format if (show_percent or show_values) else None,
        startangle=90,
        pctdistance=0.75 if donut else 0.6
    )
    
    # Style text
    for text in texts:
        text.set_fontsize(11)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # Donut effect
    if donut:
        center_circle = plt.Circle((0, 0), 0.50, fc='white')
        ax.add_patch(center_circle)
    
    # Title
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    ax.axis('equal')
    
    plt.tight_layout()
    plt.savefig(output, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate pie charts from data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple pie chart
  python pie_chart.py --labels '["Sales", "Marketing", "Engineering"]' --values '[40, 25, 35]'
  
  # Donut chart with exploded slice
  python pie_chart.py --labels '["A", "B", "C", "D"]' --values '[30, 25, 25, 20]' \\
    --donut --explode 0 --title "Market Share"
  
  # Use of funds pie
  python pie_chart.py --labels '["Engineering", "Marketing", "Operations", "Sales"]' \\
    --values '[45, 25, 15, 15]' --title "Use of Funds"
        """
    )
    
    parser.add_argument("--labels", required=True, help="JSON array of labels")
    parser.add_argument("--values", required=True, help="JSON array of values")
    parser.add_argument("--title", default="", help="Chart title")
    parser.add_argument("--colors", help="JSON array of colors")
    parser.add_argument("--donut", action="store_true", help="Donut chart (hollow center)")
    parser.add_argument("--explode", type=int, help="Index of slice to explode")
    parser.add_argument("--show-percent", action="store_true", default=True, help="Show percentages")
    parser.add_argument("--no-percent", action="store_true", help="Hide percentages")
    parser.add_argument("--show-values", action="store_true", help="Show actual values")
    parser.add_argument("--width", type=float, default=8, help="Width in inches")
    parser.add_argument("--height", type=float, default=8, help="Height in inches")
    parser.add_argument("--dpi", type=int, default=150, help="Resolution")
    parser.add_argument("--output", "-o", default="pie_chart.png", help="Output file")
    
    args = parser.parse_args()
    
    try:
        labels = json.loads(args.labels)
        values = json.loads(args.values)
        colors = json.loads(args.colors) if args.colors else None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    show_percent = not args.no_percent
    
    output = create_pie_chart(
        labels=labels,
        values=values,
        title=args.title,
        colors=colors,
        donut=args.donut,
        explode_index=args.explode,
        show_percent=show_percent,
        show_values=args.show_values,
        width=args.width,
        height=args.height,
        dpi=args.dpi,
        output=args.output
    )
    
    print(f"✅ Pie chart saved: {output}")


if __name__ == "__main__":
    main()
