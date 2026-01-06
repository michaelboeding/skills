#!/usr/bin/env python3
"""
Background Removal Script using rembg (AI-based)
Removes backgrounds from images using the U2-Net model.

Features:
- AI-based background removal (U2-Net model)
- Built-in white-to-transparent conversion (fast fallback)
- Batch processing support
- Multiple output formats (PNG, WebP)
"""

import argparse
import os
import sys
import json
from pathlib import Path


def load_env():
    """Load environment variables from .env file.

    Checks these locations in order:
    1. ~/.config/skills/.env (recommended)
    2. ~/.env (home directory)
    3. Walk up from script location (for local development)
    """
    def parse_env_file(env_file: Path):
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and value and key not in os.environ:
                            os.environ[key] = value
            return True
        return False

    # Check standard locations first
    home = Path.home()
    if parse_env_file(home / ".config" / "skills" / ".env"):
        return
    if parse_env_file(home / ".env"):
        return

    # Fall back to walking up from script location
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if parse_env_file(current / ".env"):
            return
        current = current.parent


load_env()


# Background removal methods
BG_REMOVAL_METHODS = {
    "rembg": "AI-based removal using rembg/U2-Net (high quality, runs locally)",
    "builtin": "Built-in white-to-transparent conversion (fast, may have artifacts)",
}


def remove_background_rembg(image_path: str, output_path: str = None) -> dict:
    """Remove background using rembg (AI-based, runs locally).

    Args:
        image_path: Path to input image
        output_path: Path for output image (optional, will auto-generate if not provided)

    Returns:
        dict with success status and output path, or error message
    """
    try:
        from rembg import remove
        from PIL import Image
    except ImportError:
        return {"error": "rembg not installed. Install with: pip install rembg[gpu] (or pip install rembg for CPU-only)"}

    if not Path(image_path).exists():
        return {"error": f"Image not found: {image_path}"}

    # Generate output path if not provided
    if not output_path:
        input_path = Path(image_path)
        output_path = str(input_path.parent / f"{input_path.stem}_nobg.png")

    try:
        # Load input image
        input_img = Image.open(image_path)

        # Remove background using rembg
        print(f"Removing background with rembg (AI model)...")
        output_img = remove(input_img)

        # Create output directory if needed
        output_dir = Path(output_path).parent
        if output_dir and str(output_dir) != "." and not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        # Determine format from extension
        ext = Path(output_path).suffix.lower()
        if ext == ".webp":
            output_img.save(output_path, "WEBP")
        else:
            output_img.save(output_path, "PNG")

        print(f"Background removed: {output_path}")

        return {
            "success": True,
            "file": output_path,
            "method": "rembg"
        }

    except Exception as e:
        return {"error": f"rembg background removal failed: {str(e)}"}


def remove_background_builtin(image_path: str, output_path: str = None) -> dict:
    """Remove background using built-in white-to-transparent conversion.

    This is a fast fallback that works well for images with clean white backgrounds.

    Args:
        image_path: Path to input image
        output_path: Path for output image (optional, will auto-generate if not provided)

    Returns:
        dict with success status and output path, or error message
    """
    try:
        from PIL import Image
    except ImportError:
        return {"error": "Pillow not installed. Install with: pip install Pillow"}

    if not Path(image_path).exists():
        return {"error": f"Image not found: {image_path}"}

    # Generate output path if not provided
    if not output_path:
        input_path = Path(image_path)
        output_path = str(input_path.parent / f"{input_path.stem}_nobg.png")

    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")

        # Use numpy for faster processing if available, else fall back to PIL
        try:
            import numpy as np
            data = np.array(img)

            # Calculate brightness and saturation for all pixels
            r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
            brightness = (r.astype(float) + g.astype(float) + b.astype(float)) / 3
            max_rgb = np.maximum(np.maximum(r, g), b).astype(float)
            min_rgb = np.minimum(np.minimum(r, g), b).astype(float)
            saturation = np.where(max_rgb > 0, (max_rgb - min_rgb) / max_rgb, 0)

            # Create mask for pixels to make transparent
            # Only remove if BOTH low saturation AND reasonably bright
            mask = (
                ((saturation < 0.30) & (brightness > 100)) |  # Low sat + bright = background
                (brightness > 240)                             # Pure white
            )

            # Set alpha to 0 for background pixels
            data[:, :, 3] = np.where(mask, 0, a)
            img = Image.fromarray(data)

        except ImportError:
            # Fallback to PIL if numpy not available
            pixels = img.load()
            width, height = img.size
            for y in range(height):
                for x in range(width):
                    r, g, b, a = pixels[x, y]
                    brightness = (r + g + b) / 3
                    max_rgb = max(r, g, b)
                    min_rgb = min(r, g, b)
                    saturation = (max_rgb - min_rgb) / max_rgb if max_rgb > 0 else 0

                    if (saturation < 0.30 and brightness > 100) or brightness > 240:
                        pixels[x, y] = (r, g, b, 0)

        # Create output directory if needed
        output_dir = Path(output_path).parent
        if output_dir and str(output_dir) != "." and not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        # Determine format from extension
        ext = Path(output_path).suffix.lower()
        if ext == ".webp":
            img.save(output_path, "WEBP")
        else:
            img.save(output_path, "PNG")

        print(f"Background removed: {output_path}")

        return {
            "success": True,
            "file": output_path,
            "method": "builtin"
        }

    except Exception as e:
        return {"error": f"Built-in background removal failed: {str(e)}"}


def remove_background(image_path: str, output_path: str = None, method: str = "rembg") -> dict:
    """Remove background from an image.

    This is the main entry point that delegates to the appropriate method.

    Args:
        image_path: Path to input image
        output_path: Path for output image (optional)
        method: Background removal method ("rembg" or "builtin")

    Returns:
        dict with success status and output path, or error message
    """
    if method == "rembg":
        result = remove_background_rembg(image_path, output_path)
        # Fall back to builtin if rembg fails (e.g., not installed)
        if "error" in result and "not installed" in result.get("error", ""):
            print(f"rembg not available, falling back to builtin method...")
            return remove_background_builtin(image_path, output_path)
        return result
    elif method == "builtin":
        return remove_background_builtin(image_path, output_path)
    else:
        return {"error": f"Unknown method: {method}. Use 'rembg' or 'builtin'."}


def main():
    parser = argparse.ArgumentParser(
        description="Remove backgrounds from images using AI (rembg) or built-in methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Methods:
  rembg     AI-based using U2-Net model (high quality, default)
  builtin   Fast white-to-transparent conversion (good for clean backgrounds)

Examples:
  # Remove background from a single image
  python background_remove.py -i photo.jpg

  # Specify output path
  python background_remove.py -i photo.jpg -o photo_transparent.png

  # Use built-in method (faster, for white backgrounds)
  python background_remove.py -i icon.png -m builtin

  # Batch process multiple images
  python background_remove.py -i img1.jpg img2.png img3.webp

  # Output as WebP
  python background_remove.py -i photo.jpg -o result.webp
        """
    )

    parser.add_argument("--input", "-i", nargs="+", required=True,
                        help="Input image path(s)")
    parser.add_argument("--output", "-o",
                        help="Output path (for single image) or directory (for batch)")
    parser.add_argument("--method", "-m", default="rembg",
                        choices=["rembg", "builtin"],
                        help="Background removal method (default: rembg)")

    args = parser.parse_args()

    results = []

    for input_path in args.input:
        # Determine output path
        if args.output:
            if len(args.input) > 1:
                # Batch mode: output is a directory
                output_dir = Path(args.output)
                output_dir.mkdir(parents=True, exist_ok=True)
                input_name = Path(input_path).stem
                output_path = str(output_dir / f"{input_name}_nobg.png")
            else:
                # Single file mode
                output_path = args.output
        else:
            output_path = None  # Will auto-generate

        print(f"Processing: {input_path}")
        result = remove_background(input_path, output_path, args.method)

        if "error" in result:
            print(f"  Error: {result['error']}", file=sys.stderr)
        else:
            print(f"  Saved: {result['file']}")

        results.append(result)

    # Summary
    print()
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if "error" in r]

    if successful:
        print(f"Successfully processed {len(successful)} image(s)")
    if failed:
        print(f"Failed: {len(failed)} image(s)", file=sys.stderr)
        sys.exit(1)

    # Output JSON for programmatic use
    if len(results) == 1:
        print(json.dumps(results[0], indent=2))
    else:
        print(json.dumps({"results": results}, indent=2))


if __name__ == "__main__":
    main()
