#!/usr/bin/env python3
"""
Bar Chart Generator
Generates bar charts (vertical or horizontal) from data.

Usage:
  python bar_chart.py --labels '["A", "B", "C"]' --values '[10, 20, 30]' --output chart.png
"""

import argparse
import json
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
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


def create_bar_chart(
    labels: list,
    values: list,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    colors: list = None,
    horizontal: bool = False,
    show_values: bool = True,
    width: float = 10,
    height: float = 6,
    dpi: int = 150,
    style: str = "seaborn-v0_8-whitegrid",
    output: str = "bar_chart.png"
):
    """Generate a bar chart and save to file."""
    
    # Set style
    try:
        plt.style.use(style)
    except:
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn' in plt.style.available else 'ggplot')
    
    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    
    # Default colors
    if colors is None:
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#00BCD4', '#795548']
    
    # Extend colors if needed
    while len(colors) < len(labels):
        colors = colors + colors
    colors = colors[:len(labels)]
    
    # Create bars
    if horizontal:
        bars = ax.barh(labels, values, color=colors)
        if show_values:
            for bar, val in zip(bars, values):
                ax.text(val + max(values) * 0.02, bar.get_y() + bar.get_height()/2,
                       f'{val:,.0f}' if isinstance(val, (int, float)) else str(val),
                       va='center', fontsize=10)
    else:
        bars = ax.bar(labels, values, color=colors)
        if show_values:
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, val + max(values) * 0.02,
                       f'{val:,.0f}' if isinstance(val, (int, float)) else str(val),
                       ha='center', va='bottom', fontsize=10)
    
    # Labels and title
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11)
    
    # Rotate x labels if too many
    if not horizontal and len(labels) > 5:
        plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Save
    plt.savefig(output, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate bar charts from data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple bar chart
  python bar_chart.py --labels '["A", "B", "C"]' --values '[10, 20, 30]'
  
  # Horizontal with custom colors
  python bar_chart.py --labels '["Sales", "Marketing", "Eng"]' --values '[500, 300, 700]' \\
    --horizontal --colors '["#4CAF50", "#2196F3", "#FF9800"]'
  
  # With title and labels
  python bar_chart.py --labels '["Q1", "Q2", "Q3", "Q4"]' --values '[100, 150, 200, 280]' \\
    --title "Quarterly Revenue" --ylabel "Revenue ($K)"
        """
    )
    
    parser.add_argument("--labels", required=True, help="JSON array of labels")
    parser.add_argument("--values", required=True, help="JSON array of values")
    parser.add_argument("--title", default="", help="Chart title")
    parser.add_argument("--xlabel", default="", help="X-axis label")
    parser.add_argument("--ylabel", default="", help="Y-axis label")
    parser.add_argument("--colors", help="JSON array of colors")
    parser.add_argument("--horizontal", action="store_true", help="Horizontal bars")
    parser.add_argument("--show-values", action="store_true", default=True, help="Show values on bars")
    parser.add_argument("--no-values", action="store_true", help="Hide values on bars")
    parser.add_argument("--width", type=float, default=10, help="Width in inches")
    parser.add_argument("--height", type=float, default=6, help="Height in inches")
    parser.add_argument("--dpi", type=int, default=150, help="Resolution")
    parser.add_argument("--style", default="seaborn-v0_8-whitegrid", help="Matplotlib style")
    parser.add_argument("--output", "-o", default="bar_chart.png", help="Output file")
    
    args = parser.parse_args()
    
    # Parse JSON inputs
    try:
        labels = json.loads(args.labels)
        values = json.loads(args.values)
        colors = json.loads(args.colors) if args.colors else None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    if len(labels) != len(values):
        print("Error: labels and values must have the same length", file=sys.stderr)
        sys.exit(1)
    
    show_values = not args.no_values
    
    output = create_bar_chart(
        labels=labels,
        values=values,
        title=args.title,
        xlabel=args.xlabel,
        ylabel=args.ylabel,
        colors=colors,
        horizontal=args.horizontal,
        show_values=show_values,
        width=args.width,
        height=args.height,
        dpi=args.dpi,
        style=args.style,
        output=args.output
    )
    
    print(f"✅ Bar chart saved: {output}")


if __name__ == "__main__":
    main()
