#!/usr/bin/env python3
"""
TAM/SAM/SOM Chart Generator
Generates market size visualization with concentric circles.

Usage:
  python tam_sam_som.py --tam 50 --sam 8 --som 0.5 --unit "B" --output market.png
"""

import argparse
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    print("Error: matplotlib not installed. Run: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def create_tam_sam_som(
    tam: float,
    sam: float,
    som: float,
    unit: str = "B",
    title: str = "Market Opportunity",
    labels: list = None,
    colors: list = None,
    width: float = 10,
    height: float = 10,
    dpi: int = 150,
    output: str = "tam_sam_som.png"
):
    """Generate a TAM/SAM/SOM chart with concentric circles."""
    
    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    
    # Default colors (light to dark)
    if colors is None:
        colors = ['#bbdefb', '#64b5f6', '#1976d2']  # Light blue to dark blue
    
    # Default labels
    if labels is None:
        labels = ['TAM', 'SAM', 'SOM']
    
    # Normalize sizes for visualization
    max_size = tam
    tam_radius = 1.0
    sam_radius = (sam / max_size) ** 0.5  # Square root for area proportion
    som_radius = (som / max_size) ** 0.5
    
    # Minimum visible radius
    sam_radius = max(sam_radius, 0.2)
    som_radius = max(som_radius, 0.08)
    
    # Draw circles (largest first)
    circles = [
        (tam_radius, colors[0], f'{labels[0]}\n${tam:,.1f}{unit}', tam),
        (sam_radius, colors[1], f'{labels[1]}\n${sam:,.1f}{unit}', sam),
        (som_radius, colors[2], f'{labels[2]}\n${som:,.1f}{unit}', som),
    ]
    
    for radius, color, label, value in circles:
        circle = plt.Circle((0, 0), radius, color=color, ec='white', linewidth=3)
        ax.add_patch(circle)
    
    # Add labels
    # TAM label at top
    ax.text(0, tam_radius * 0.75, f'{labels[0]}', ha='center', va='center',
           fontsize=14, fontweight='bold', color='#333')
    ax.text(0, tam_radius * 0.60, f'${tam:,.1f}{unit}', ha='center', va='center',
           fontsize=12, color='#555')
    
    # SAM label
    if sam_radius > 0.3:
        ax.text(0, -sam_radius * 0.5, f'{labels[1]}', ha='center', va='center',
               fontsize=12, fontweight='bold', color='white')
        ax.text(0, -sam_radius * 0.7, f'${sam:,.1f}{unit}', ha='center', va='center',
               fontsize=10, color='white')
    
    # SOM label (outside if too small)
    if som_radius > 0.15:
        ax.text(0, 0, f'{labels[2]}\n${som:,.1f}{unit}', ha='center', va='center',
               fontsize=10, fontweight='bold', color='white')
    else:
        ax.annotate(f'{labels[2]}: ${som:,.1f}{unit}', xy=(0, 0), 
                   xytext=(0.8, -0.8), fontsize=10, fontweight='bold',
                   arrowprops=dict(arrowstyle='->', color='#333'))
    
    # Set limits
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Legend
    legend_elements = [
        mpatches.Patch(color=colors[0], label=f'{labels[0]} (Total Addressable Market)'),
        mpatches.Patch(color=colors[1], label=f'{labels[1]} (Serviceable Addressable Market)'),
        mpatches.Patch(color=colors[2], label=f'{labels[2]} (Serviceable Obtainable Market)'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, -0.05))
    
    plt.tight_layout()
    plt.savefig(output, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate TAM/SAM/SOM market size charts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic market size chart (billions)
  python tam_sam_som.py --tam 50 --sam 8 --som 0.5
  
  # With millions
  python tam_sam_som.py --tam 500 --sam 75 --som 10 --unit "M"
  
  # Custom labels
  python tam_sam_som.py --tam 100 --sam 20 --som 5 \\
    --labels '["Global Market", "US Market", "Target Segment"]'
        """
    )
    
    parser.add_argument("--tam", type=float, required=True, help="Total Addressable Market size")
    parser.add_argument("--sam", type=float, required=True, help="Serviceable Addressable Market size")
    parser.add_argument("--som", type=float, required=True, help="Serviceable Obtainable Market size")
    parser.add_argument("--unit", default="B", help="Unit: 'B' for billions, 'M' for millions")
    parser.add_argument("--title", default="Market Opportunity", help="Chart title")
    parser.add_argument("--labels", help="JSON array of 3 labels (default: TAM, SAM, SOM)")
    parser.add_argument("--colors", help="JSON array of 3 colors (outer to inner)")
    parser.add_argument("--width", type=float, default=10, help="Width in inches")
    parser.add_argument("--height", type=float, default=10, help="Height in inches")
    parser.add_argument("--dpi", type=int, default=150, help="Resolution")
    parser.add_argument("--output", "-o", default="tam_sam_som.png", help="Output file")
    
    args = parser.parse_args()
    
    try:
        labels = json.loads(args.labels) if args.labels else None
        colors = json.loads(args.colors) if args.colors else None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate hierarchy
    if not (args.tam >= args.sam >= args.som):
        print("Warning: TAM should be >= SAM >= SOM", file=sys.stderr)
    
    output = create_tam_sam_som(
        tam=args.tam,
        sam=args.sam,
        som=args.som,
        unit=args.unit,
        title=args.title,
        labels=labels,
        colors=colors,
        width=args.width,
        height=args.height,
        dpi=args.dpi,
        output=args.output
    )
    
    print(f"✅ TAM/SAM/SOM chart saved: {output}")


if __name__ == "__main__":
    import json
    main()
