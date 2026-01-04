#!/usr/bin/env python3
"""
Line Chart Generator
Generates line charts for trends and time series data.

Usage:
  python line_chart.py --x '["Jan", "Feb", "Mar"]' --y '[100, 150, 200]' --output chart.png
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


def create_line_chart(
    x: list,
    y: list,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    legend: list = None,
    colors: list = None,
    fill: bool = False,
    markers: bool = True,
    width: float = 10,
    height: float = 6,
    dpi: int = 150,
    style: str = "seaborn-v0_8-whitegrid",
    output: str = "line_chart.png"
):
    """Generate a line chart and save to file."""
    
    try:
        plt.style.use(style)
    except:
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn' in plt.style.available else 'ggplot')
    
    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    
    # Default colors
    if colors is None:
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0']
    
    # Handle single or multiple series
    if y and isinstance(y[0], list):
        # Multiple series
        for i, series in enumerate(y):
            color = colors[i % len(colors)]
            label = legend[i] if legend and i < len(legend) else f"Series {i+1}"
            line, = ax.plot(x, series, color=color, linewidth=2, 
                           marker='o' if markers else None, markersize=6, label=label)
            if fill:
                ax.fill_between(x, series, alpha=0.3, color=color)
        ax.legend(loc='best')
    else:
        # Single series
        color = colors[0]
        ax.plot(x, y, color=color, linewidth=2, marker='o' if markers else None, markersize=6)
        if fill:
            ax.fill_between(x, y, alpha=0.3, color=color)
    
    # Labels and title
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11)
    
    # Rotate x labels if needed
    if len(x) > 8:
        plt.xticks(rotation=45, ha='right')
    
    # Grid
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate line charts from data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple line chart
  python line_chart.py --x '["Jan", "Feb", "Mar", "Apr"]' --y '[100, 150, 200, 280]'
  
  # Multiple series
  python line_chart.py --x '["Q1", "Q2", "Q3", "Q4"]' \\
    --y '[[100, 150, 200, 280], [80, 120, 180, 250]]' \\
    --legend '["Revenue", "Profit"]'
  
  # With fill and styling
  python line_chart.py --x '["Jan", "Feb", "Mar"]' --y '[50, 100, 180]' \\
    --title "Growth Trend" --ylabel "Users (K)" --fill
        """
    )
    
    parser.add_argument("--x", required=True, help="JSON array of x-axis values")
    parser.add_argument("--y", required=True, help="JSON array of y values (or array of arrays for multi-series)")
    parser.add_argument("--title", default="", help="Chart title")
    parser.add_argument("--xlabel", default="", help="X-axis label")
    parser.add_argument("--ylabel", default="", help="Y-axis label")
    parser.add_argument("--legend", help="JSON array of legend labels for multi-series")
    parser.add_argument("--colors", help="JSON array of colors")
    parser.add_argument("--fill", action="store_true", help="Fill area under line")
    parser.add_argument("--markers", action="store_true", default=True, help="Show data point markers")
    parser.add_argument("--no-markers", action="store_true", help="Hide markers")
    parser.add_argument("--width", type=float, default=10, help="Width in inches")
    parser.add_argument("--height", type=float, default=6, help="Height in inches")
    parser.add_argument("--dpi", type=int, default=150, help="Resolution")
    parser.add_argument("--style", default="seaborn-v0_8-whitegrid", help="Matplotlib style")
    parser.add_argument("--output", "-o", default="line_chart.png", help="Output file")
    
    args = parser.parse_args()
    
    try:
        x = json.loads(args.x)
        y = json.loads(args.y)
        legend = json.loads(args.legend) if args.legend else None
        colors = json.loads(args.colors) if args.colors else None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    markers = not args.no_markers
    
    output = create_line_chart(
        x=x,
        y=y,
        title=args.title,
        xlabel=args.xlabel,
        ylabel=args.ylabel,
        legend=legend,
        colors=colors,
        fill=args.fill,
        markers=markers,
        width=args.width,
        height=args.height,
        dpi=args.dpi,
        style=args.style,
        output=args.output
    )
    
    print(f"✅ Line chart saved: {output}")


if __name__ == "__main__":
    main()
