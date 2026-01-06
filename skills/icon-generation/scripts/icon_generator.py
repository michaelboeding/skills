#!/usr/bin/env python3
"""
Icon Generation Script using Google Gemini
Generates app icons with transparent backgrounds.

Requires: GOOGLE_API_KEY environment variable

Features:
- Transparent PNG output
- Multiple size generation
- Style presets (flat, 3d, line, glyph, gradient, minimal)
- Batch generation for icon sets
- Reference image support for style consistency across icon sets
"""

import argparse
import os
import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import base64
from datetime import datetime
from pathlib import Path


# Style presets with prompt modifiers
STYLE_MODIFIERS = {
    "flat": "flat design, solid colors, no gradients, minimal shadows, clean vector style",
    "3d": "3D style, depth, soft shadows, subtle gradients, professional rendering",
    "line": "line art, outline only, thin consistent strokes, no fill, minimalist",
    "glyph": "solid filled shape, single color, bold silhouette, high contrast",
    "gradient": "smooth gradient colors, modern vibrant transitions, glossy finish",
    "minimal": "ultra-minimal, essential shapes only, maximum simplicity, geometric",
}

# Common icon sizes
COMMON_SIZES = [16, 32, 64, 128, 180, 192, 256, 512, 1024]


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


def load_image_as_base64(image_path: str) -> tuple:
    """Load an image file and return base64 data and mime type."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    suffix = path.suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    mime_type = mime_types.get(suffix, "image/png")

    with open(path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    return image_data, mime_type


def get_image_dimensions(image_path: str) -> tuple:
    """Get dimensions of an image file. Returns (width, height)."""
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            return img.size
    except ImportError:
        # PIL not available, return None
        return None
    except Exception:
        return None


# Supported output formats
OUTPUT_FORMATS = {
    "png": {"ext": ".png", "pil_format": "PNG", "description": "PNG with transparency support"},
    "jpeg": {"ext": ".jpg", "pil_format": "JPEG", "description": "JPEG (no transparency, smaller file)"},
    "jpg": {"ext": ".jpg", "pil_format": "JPEG", "description": "JPEG (no transparency, smaller file)"},
    "webp": {"ext": ".webp", "pil_format": "WEBP", "description": "WebP (modern format, good compression)"},
}

# Background removal methods
BG_REMOVAL_METHODS = {
    "builtin": "Built-in white-to-transparent conversion (fast, may have artifacts)",
    "rembg": "AI-based removal using rembg/U2-Net (high quality, runs locally)",
    "none": "No background removal (keep as-is from Gemini)",
}


def get_background_remove_module():
    """Import the background_remove module from the background-remove skill."""
    # Find the background-remove skill relative to this script
    skill_root = Path(__file__).resolve().parent.parent.parent
    bg_remove_path = skill_root / "background-remove" / "scripts"

    if bg_remove_path.exists():
        import sys
        if str(bg_remove_path) not in sys.path:
            sys.path.insert(0, str(bg_remove_path))
        from background_remove import remove_background
        return remove_background
    else:
        return None


def build_icon_prompt(concept: str, style: str, colors: str = None, has_reference: bool = False) -> str:
    """Build an optimized prompt for icon generation."""
    style_modifier = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["flat"])

    if has_reference:
        # When reference image provided, emphasize style matching
        prompt_parts = [
            f"Create an icon of {concept} that EXACTLY matches the style of the reference image",
            "Match the same visual style, line weight, color palette, and design language",
            "Place the icon on a plain solid pure white (#FFFFFF) background",
            "NO shadows, NO gradients on background, NO drop shadows, completely flat background",
            "Square format, perfectly centered, clean crisp edges",
            "The new icon should look like it belongs in the same icon set as the reference",
        ]
    else:
        prompt_parts = [
            f"A {style} style icon of {concept}",
            "on a plain solid pure white (#FFFFFF) background",
            "NO shadows, NO gradients on background, NO drop shadows",
            "Square format, perfectly centered, clean crisp edges",
            "Suitable for app icon or favicon",
            style_modifier,
            "Simple, instantly recognizable, professional quality",
        ]

    if colors:
        prompt_parts.append(f"Color scheme: {colors}")

    return ". ".join(prompt_parts) + "."


def generate_icon(prompt: str, size: int = 512, output_path: str = None,
                  reference_images: list = None, output_format: str = "png",
                  bg_removal: str = "builtin") -> dict:
    """Generate a single icon using Google Gemini.

    Args:
        prompt: Full icon generation prompt
        size: Output size in pixels (square)
        output_path: Output file path
        reference_images: List of reference image paths for style matching
        output_format: Output format (png, jpeg, webp)
        bg_removal: Background removal method (builtin, rembg, none)
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY environment variable not set. Get your key at https://aistudio.google.com/apikey"}

    # Use Nano Banana Pro for best quality (supports up to 14 reference images)
    model = "gemini-3-pro-image-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    headers = {"Content-Type": "application/json"}

    # Determine resolution based on size
    if size >= 1024:
        resolution = "2K"  # Higher res for large icons
    else:
        resolution = "1K"

    # Build content parts - start with text prompt
    parts = [{"text": prompt}]

    # Add reference images if provided
    if reference_images:
        for img_path in reference_images:
            try:
                img_data, mime_type = load_image_as_base64(img_path)
                parts.append({
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": img_data
                    }
                })
            except FileNotFoundError as e:
                return {"error": str(e)}
            except Exception as e:
                return {"error": f"Failed to load reference image {img_path}: {str(e)}"}

    data = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "imageConfig": {
                "aspectRatio": "1:1",  # Always square for icons
                "imageSize": resolution
            }
        }
    }

    try:
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode())

            candidates = result.get("candidates", [])
            if not candidates:
                return {"error": "No response generated. Try a different prompt."}

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])

            if not parts:
                return {"error": "No content in response"}

            # Extract image data
            image_data = None
            for part in parts:
                if part.get("thought"):
                    continue
                if "inlineData" in part:
                    image_data = part["inlineData"].get("data")
                    break

            if not image_data:
                return {"error": "No image generated. Try a simpler concept."}

            # Get format info
            fmt = OUTPUT_FORMATS.get(output_format.lower(), OUTPUT_FORMATS["png"])
            ext = fmt["ext"]

            # Determine output filename
            if output_path:
                filename = output_path
                # Replace or add correct extension
                base = str(Path(output_path).with_suffix(""))
                if not any(output_path.lower().endswith(e) for e in [".png", ".jpg", ".jpeg", ".webp"]):
                    filename = f"{base}_{size}{ext}"
                else:
                    filename = f"{base}{ext}"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"icon_{timestamp}_{size}{ext}"

            # Create parent directory if needed
            output_dir = Path(filename).parent
            if output_dir and str(output_dir) != "." and not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)

            # Save raw image data first (Gemini returns PNG)
            temp_file = filename + ".tmp"
            with open(temp_file, "wb") as f:
                f.write(base64.b64decode(image_data))

            # Post-process: resize, remove background, convert format
            try:
                from PIL import Image
                img = Image.open(temp_file)

                # Resize if needed
                if img.size[0] != size:
                    img = img.resize((size, size), Image.Resampling.LANCZOS)

                # Handle background removal based on method
                print(f"  Background removal method: {bg_removal}", file=sys.stderr)
                if output_format.lower() in ["png", "webp"] and bg_removal != "none":
                    print(f"  Entering bg removal block", file=sys.stderr)

                    # Use the background-remove skill for both rembg and builtin methods
                    remove_background = get_background_remove_module()

                    if remove_background:
                        # Save the resized image first
                        temp_resized = temp_file + ".resized.png"
                        img.save(temp_resized, "PNG")

                        print(f"  Using background-remove skill ({bg_removal} method)...")
                        bg_result = remove_background(temp_resized, filename, method=bg_removal)

                        if "error" in bg_result:
                            error_msg = bg_result.get("error", "")
                            print(f"  Background removal failed: {error_msg}", file=sys.stderr)
                            # Just save without background removal
                            img.save(filename, fmt["pil_format"])
                            Path(temp_resized).unlink(missing_ok=True)
                            Path(temp_file).unlink(missing_ok=True)
                        else:
                            # Background removal succeeded
                            Path(temp_resized).unlink(missing_ok=True)
                            Path(temp_file).unlink(missing_ok=True)
                            result_data = {
                                "success": True,
                                "file": filename,
                                "size": size,
                                "format": output_format,
                                "prompt": prompt,
                                "bg_removal": bg_result.get("method", bg_removal)
                            }
                            if reference_images:
                                result_data["reference_images"] = reference_images
                            return result_data
                    else:
                        # background-remove skill not found, save without removal
                        print("  Warning: background-remove skill not found", file=sys.stderr)
                        img.save(filename, fmt["pil_format"])
                else:
                    # For JPEG or no bg removal, just convert and save
                    if output_format.lower() in ["jpeg", "jpg"]:
                        img = img.convert("RGB")
                        img.save(filename, fmt["pil_format"], quality=95)
                    else:
                        img.save(filename, fmt["pil_format"])

                # Remove temp file
                Path(temp_file).unlink(missing_ok=True)
            except ImportError:
                # PIL not available, just rename temp file
                Path(temp_file).rename(filename)
            except Exception as e:
                # On error, keep temp file as output
                if Path(temp_file).exists():
                    Path(temp_file).rename(filename)

            result_data = {
                "success": True,
                "file": filename,
                "size": size,
                "format": output_format,
                "prompt": prompt,
                "bg_removal": bg_removal
            }

            if reference_images:
                result_data["reference_images"] = reference_images

            return result_data

    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        try:
            error_json = json.loads(error_body)
            error_message = error_json.get("error", {}).get("message", error_body)
        except:
            error_message = error_body
        return {"error": f"API error ({e.code}): {error_message}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(
        description="Generate app icons with transparent backgrounds using Google Gemini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Styles:
  flat      Modern flat design, solid colors (default)
  3d        Depth and shadows, premium look
  line      Outline only, minimalist
  glyph     Solid filled shape, single color
  gradient  Smooth color transitions
  minimal   Ultra-simple, essential shapes only

Formats:
  png       PNG with transparency (default)
  jpeg/jpg  JPEG (no transparency, smaller file)
  webp      WebP (modern format, good compression)

Examples:
  # Single icon
  python icon_generator.py -p "shopping cart" -s flat -z 512

  # Multiple sizes
  python icon_generator.py -p "music note" -s gradient -z 1024 512 256 128

  # Different output format
  python icon_generator.py -p "camera" -s 3d -z 512 -f webp

  # Batch generation
  python icon_generator.py -b '["home", "search", "profile"]' -s flat -z 512

  # With reference image (auto-detects size from reference)
  python icon_generator.py -p "settings gear" -r existing_icon.png

  # Batch with reference (consistent icon set)
  python icon_generator.py -b '["home", "search", "profile"]' -r brand_icon.png
        """
    )

    parser.add_argument("--prompt", "-p", help="Icon concept or description")
    parser.add_argument("--style", "-s", default="flat",
                        choices=list(STYLE_MODIFIERS.keys()),
                        help="Icon style preset (default: flat)")
    parser.add_argument("--size", "-z", type=int, nargs="+", default=None,
                        help="Size(s) in pixels (default: 512, or auto from reference)")
    parser.add_argument("--format", "-f", default="png",
                        choices=["png", "jpeg", "jpg", "webp"],
                        help="Output format (default: png)")
    parser.add_argument("--output", "-o", help="Output path (without extension for multi-size)")
    parser.add_argument("--batch", "-b", help="JSON array of concepts for batch generation")
    parser.add_argument("--colors", "-c", help="Color preferences (e.g., 'blue and white')")
    parser.add_argument("--reference", "-r", action="append", dest="references",
                        help="Reference image(s) for style matching (can be used multiple times)")
    parser.add_argument("--bg-removal", "--bg", default="builtin",
                        choices=["builtin", "rembg", "none"],
                        help="Background removal method: builtin (fast), rembg (AI-based, high quality), none (default: builtin)")

    args = parser.parse_args()

    # Validate input
    if not args.prompt and not args.batch:
        parser.error("Either --prompt or --batch is required")

    results = []
    has_reference = bool(args.references)

    # Auto-detect size from reference image if not specified
    sizes = args.size
    if sizes is None:
        if has_reference:
            # Try to get dimensions from first reference image
            dims = get_image_dimensions(args.references[0])
            if dims:
                # Use the smaller dimension (for square icons)
                ref_size = min(dims[0], dims[1])
                sizes = [ref_size]
                print(f"Auto-detected size from reference: {ref_size}px")
            else:
                sizes = [512]  # Default if can't read image
        else:
            sizes = [512]  # Default size

    if args.batch:
        # Batch mode: generate multiple icons
        try:
            concepts = json.loads(args.batch)
            if not isinstance(concepts, list):
                print("Error: --batch must be a JSON array", file=sys.stderr)
                sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in --batch: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"Generating {len(concepts)} icons in {args.style} style...")
        print(f"Format: {args.format.upper()}")
        print(f"Background removal: {args.bg_removal}")
        if has_reference:
            print(f"Using {len(args.references)} reference image(s) for style matching")
        print()

        for concept in concepts:
            prompt = build_icon_prompt(concept, args.style, args.colors, has_reference)

            for size in sizes:
                if args.output:
                    output_path = f"{args.output}/{concept}_{size}"
                else:
                    output_path = f"{concept}_{size}"

                print(f"Generating: {concept} ({size}px)...")
                result = generate_icon(prompt, size, output_path, args.references, args.format, args.bg_removal)

                if "error" in result:
                    print(f"  Error: {result['error']}", file=sys.stderr)
                else:
                    print(f"  Saved: {result['file']}")

                results.append(result)

    else:
        # Single concept mode
        prompt = build_icon_prompt(args.prompt, args.style, args.colors, has_reference)

        print(f"Generating icon: {args.prompt}")
        print(f"Style: {args.style}")
        print(f"Format: {args.format.upper()}")
        print(f"Background removal: {args.bg_removal}")
        print(f"Sizes: {sizes}")
        if has_reference:
            print(f"Reference images: {len(args.references)}")
            for ref in args.references:
                print(f"  - {ref}")
        print()

        for size in sizes:
            if args.output:
                if len(sizes) > 1:
                    # Multiple sizes: add size suffix
                    base = str(Path(args.output).with_suffix(""))
                    output_path = f"{base}_{size}"
                else:
                    # Single size: use as-is
                    output_path = str(Path(args.output).with_suffix(""))
            else:
                output_path = None

            print(f"Generating {size}px icon...")
            result = generate_icon(prompt, size, output_path, args.references, args.format, args.bg_removal)

            if "error" in result:
                print(f"Error: {result['error']}", file=sys.stderr)
            else:
                print(f"Saved: {result['file']}")

            results.append(result)

    # Summary
    print()
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if "error" in r]

    if successful:
        print(f"Successfully generated {len(successful)} icon(s)")
    if failed:
        print(f"Failed: {len(failed)} icon(s)", file=sys.stderr)
        sys.exit(1)

    # Output JSON for programmatic use
    if len(results) == 1:
        print(json.dumps(results[0], indent=2))
    else:
        print(json.dumps({"results": results}, indent=2))


if __name__ == "__main__":
    main()
