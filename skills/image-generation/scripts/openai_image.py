#!/usr/bin/env python3
"""
OpenAI GPT Image Generation Script
Supports: gpt-image-1.5, gpt-image-1, gpt-image-1-mini

Features:
- Text-to-image generation
- Image editing with reference images (up to 16)
- Inpainting with masks
- Transparent backgrounds
- Streaming with partial images
- Multiple output formats and compression

Requires: OPENAI_API_KEY environment variable
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
import mimetypes


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

    home = Path.home()
    if parse_env_file(home / ".config" / "skills" / ".env"):
        return
    if parse_env_file(home / ".env"):
        return

    current = Path(__file__).resolve().parent
    for _ in range(10):
        if parse_env_file(current / ".env"):
            return
        current = current.parent


load_env()


def get_mime_type(file_path: str) -> str:
    """Get MIME type for a file."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        suffix = Path(file_path).suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mime_type = mime_map.get(suffix, "image/png")
    return mime_type


def load_image_bytes(image_path: str) -> bytes:
    """Load an image file and return raw bytes."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(path, "rb") as f:
        return f.read()


def generate_image(prompt: str, model: str = "gpt-image-1",
                   size: str = "auto", quality: str = "auto",
                   background: str = "auto", output_format: str = "png",
                   compression: int = None, n: int = 1,
                   moderation: str = "auto", output_path: str = None) -> dict:
    """Generate an image using OpenAI GPT Image API (generations endpoint).

    Args:
        prompt: Text prompt for image generation (up to 32,000 chars)
        model: Model to use (gpt-image-1.5, gpt-image-1, gpt-image-1-mini)
        size: Image size (1024x1024, 1536x1024, 1024x1536, auto)
        quality: Quality level (low, medium, high, auto)
        background: Background type (transparent, opaque, auto)
        output_format: Output format (png, jpeg, webp)
        compression: Compression level 0-100 (for jpeg/webp only)
        n: Number of images to generate (1-10)
        moderation: Moderation level (auto, low)
        output_path: Output file path (optional)
    """

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY environment variable not set. Get your key at https://platform.openai.com/api-keys"}

    # Validate model
    valid_models = ["gpt-image-1.5", "gpt-image-1", "gpt-image-1-mini"]
    if model not in valid_models:
        return {"error": f"Invalid model. Must be one of: {valid_models}"}

    # Validate size
    valid_sizes = ["1024x1024", "1536x1024", "1024x1536", "auto"]
    if size not in valid_sizes:
        return {"error": f"Invalid size. Must be one of: {valid_sizes}"}

    # Validate quality
    valid_qualities = ["low", "medium", "high", "auto"]
    if quality not in valid_qualities:
        return {"error": f"Invalid quality. Must be one of: {valid_qualities}"}

    # Validate background
    valid_backgrounds = ["transparent", "opaque", "auto"]
    if background not in valid_backgrounds:
        return {"error": f"Invalid background. Must be one of: {valid_backgrounds}"}

    # Validate output format
    valid_formats = ["png", "jpeg", "webp"]
    if output_format not in valid_formats:
        return {"error": f"Invalid output format. Must be one of: {valid_formats}"}

    # Transparent background requires png or webp
    if background == "transparent" and output_format == "jpeg":
        return {"error": "Transparent background requires png or webp format, not jpeg"}

    # Validate compression
    if compression is not None:
        if output_format not in ["jpeg", "webp"]:
            return {"error": "Compression is only supported for jpeg and webp formats"}
        if not (0 <= compression <= 100):
            return {"error": "Compression must be between 0 and 100"}

    # Validate n
    if not (1 <= n <= 10):
        return {"error": "Number of images (n) must be between 1 and 10"}

    # Validate moderation
    valid_moderation = ["auto", "low"]
    if moderation not in valid_moderation:
        return {"error": f"Invalid moderation. Must be one of: {valid_moderation}"}

    # Prepare request
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size,
        "quality": quality,
        "background": background,
        "output_format": output_format,
        "moderation": moderation
    }

    # Add compression if specified
    if compression is not None:
        data["output_compression"] = compression

    try:
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode())

            images = []
            for i, img_data in enumerate(result.get("data", [])):
                image_base64 = img_data.get("b64_json")
                revised_prompt = img_data.get("revised_prompt", prompt)

                if image_base64:
                    # Determine output filename
                    if output_path:
                        if n == 1:
                            filename = output_path
                        else:
                            base, ext = os.path.splitext(output_path)
                            filename = f"{base}_{i+1}{ext}"
                    else:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        ext = "." + output_format
                        filename = f"openai_{model.replace('-', '_')}_{timestamp}_{i+1}{ext}"

                    # Create parent directories if needed
                    output_dir = Path(filename).parent
                    if output_dir and str(output_dir) != "." and not output_dir.exists():
                        output_dir.mkdir(parents=True, exist_ok=True)

                    # Save the image
                    with open(filename, "wb") as f:
                        f.write(base64.b64decode(image_base64))

                    images.append({
                        "file": filename,
                        "revised_prompt": revised_prompt
                    })

            return {
                "success": True,
                "images": images,
                "model": model,
                "size": size,
                "quality": quality,
                "background": background,
                "output_format": output_format,
                "prompt": prompt
            }

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


def edit_image(prompt: str, images: list, mask: str = None,
               model: str = "gpt-image-1", size: str = "auto",
               quality: str = "auto", background: str = "auto",
               output_format: str = "png", compression: int = None,
               input_fidelity: str = "low", n: int = 1,
               output_path: str = None) -> dict:
    """Edit images using OpenAI GPT Image API (edits endpoint).

    Args:
        prompt: Text prompt describing the edit
        images: List of image file paths (up to 16)
        mask: Optional mask image path for inpainting
        model: Model to use
        size: Output size
        quality: Quality level
        background: Background type
        output_format: Output format
        compression: Compression level
        input_fidelity: Input fidelity (low, high) - high preserves faces/logos better
        n: Number of images to generate
        output_path: Output file path
    """

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY environment variable not set. Get your key at https://platform.openai.com/api-keys"}

    # Validate images
    if not images:
        return {"error": "At least one image is required for editing"}
    if len(images) > 16:
        return {"error": "Maximum 16 images allowed for GPT Image models"}

    # Validate input_fidelity
    valid_fidelity = ["low", "high"]
    if input_fidelity not in valid_fidelity:
        return {"error": f"Invalid input_fidelity. Must be one of: {valid_fidelity}"}

    # gpt-image-1-mini doesn't support high fidelity
    if model == "gpt-image-1-mini" and input_fidelity == "high":
        return {"error": "gpt-image-1-mini does not support high input fidelity"}

    # Build multipart form data
    import uuid
    boundary = str(uuid.uuid4())

    body_parts = []

    def add_field(name, value):
        body_parts.append(f'--{boundary}\r\n'.encode())
        body_parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body_parts.append(f'{value}\r\n'.encode())

    def add_file(name, filepath, content):
        mime_type = get_mime_type(filepath)
        filename = Path(filepath).name
        body_parts.append(f'--{boundary}\r\n'.encode())
        body_parts.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode())
        body_parts.append(f'Content-Type: {mime_type}\r\n\r\n'.encode())
        body_parts.append(content)
        body_parts.append(b'\r\n')

    # Add fields
    add_field("model", model)
    add_field("prompt", prompt)
    add_field("n", str(n))
    add_field("size", size)
    add_field("quality", quality)
    add_field("background", background)
    add_field("output_format", output_format)
    add_field("input_fidelity", input_fidelity)

    if compression is not None:
        add_field("output_compression", str(compression))

    # Add images
    for img_path in images:
        try:
            img_bytes = load_image_bytes(img_path)
            add_file("image[]", img_path, img_bytes)
        except FileNotFoundError as e:
            return {"error": str(e)}

    # Add mask if provided
    if mask:
        try:
            mask_bytes = load_image_bytes(mask)
            add_file("mask", mask, mask_bytes)
        except FileNotFoundError as e:
            return {"error": str(e)}

    body_parts.append(f'--{boundary}--\r\n'.encode())
    body = b''.join(body_parts)

    url = "https://api.openai.com/v1/images/edits"
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        request = Request(url, data=body, headers=headers, method="POST")
        with urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode())

            output_images = []
            for i, img_data in enumerate(result.get("data", [])):
                image_base64 = img_data.get("b64_json")
                revised_prompt = img_data.get("revised_prompt", prompt)

                if image_base64:
                    if output_path:
                        if n == 1:
                            filename = output_path
                        else:
                            base, ext = os.path.splitext(output_path)
                            filename = f"{base}_{i+1}{ext}"
                    else:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        ext = "." + output_format
                        filename = f"openai_edit_{timestamp}_{i+1}{ext}"

                    output_dir = Path(filename).parent
                    if output_dir and str(output_dir) != "." and not output_dir.exists():
                        output_dir.mkdir(parents=True, exist_ok=True)

                    with open(filename, "wb") as f:
                        f.write(base64.b64decode(image_base64))

                    output_images.append({
                        "file": filename,
                        "revised_prompt": revised_prompt
                    })

            return {
                "success": True,
                "images": output_images,
                "model": model,
                "input_images": images,
                "mask": mask,
                "input_fidelity": input_fidelity,
                "prompt": prompt
            }

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


def generate_streaming(prompt: str, model: str = "gpt-image-1",
                       size: str = "auto", quality: str = "auto",
                       partial_images: int = 2, output_path: str = None) -> dict:
    """Generate an image with streaming (partial images).

    Args:
        prompt: Text prompt
        model: Model to use
        size: Image size
        quality: Quality level
        partial_images: Number of partial images (0-3)
        output_path: Output file path
    """

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY environment variable not set."}

    if not (0 <= partial_images <= 3):
        return {"error": "partial_images must be between 0 and 3"}

    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "stream": True,
        "partial_images": partial_images
    }

    try:
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=300) as response:
            partial_files = []
            final_image = None

            # Read streaming response
            buffer = ""
            for chunk in iter(lambda: response.read(4096).decode('utf-8', errors='ignore'), ''):
                buffer += chunk

                # Process complete events
                while "\n\n" in buffer:
                    event, buffer = buffer.split("\n\n", 1)

                    if event.startswith("data: "):
                        event_data = event[6:]
                        if event_data == "[DONE]":
                            continue

                        try:
                            event_json = json.loads(event_data)
                            event_type = event_json.get("type", "")

                            if event_type == "image_generation.partial_image":
                                idx = event_json.get("partial_image_index", 0)
                                b64 = event_json.get("b64_json", "")

                                if b64:
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    partial_file = f"partial_{idx}_{timestamp}.png"
                                    with open(partial_file, "wb") as f:
                                        f.write(base64.b64decode(b64))
                                    partial_files.append(partial_file)
                                    print(f"Partial image {idx}: {partial_file}")

                            elif event_type == "image_generation.image":
                                b64 = event_json.get("b64_json", "")
                                if b64:
                                    if output_path:
                                        filename = output_path
                                    else:
                                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                        filename = f"openai_{model.replace('-', '_')}_{timestamp}.png"

                                    with open(filename, "wb") as f:
                                        f.write(base64.b64decode(b64))
                                    final_image = filename

                        except json.JSONDecodeError:
                            pass

            if final_image:
                return {
                    "success": True,
                    "file": final_image,
                    "partial_images": partial_files,
                    "model": model,
                    "prompt": prompt
                }
            else:
                return {"error": "No final image received from streaming"}

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
        description="Generate and edit images using OpenAI GPT Image models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Models:
  gpt-image-1.5   State of the art quality (recommended)
  gpt-image-1     Great quality, cost-effective
  gpt-image-1-mini  Fastest, most affordable

Examples:
  # Text-to-image generation
  python openai_image.py -p "A cat in space" -m gpt-image-1 -q high

  # With transparent background
  python openai_image.py -p "A product icon" --background transparent -f png

  # Image editing with reference images
  python openai_image.py -p "Add a hat to this cat" --image cat.jpg --input-fidelity high

  # Multiple reference images
  python openai_image.py -p "Create a gift basket" --image item1.png --image item2.png

  # Inpainting with mask
  python openai_image.py -p "Replace with a garden" --image scene.jpg --mask mask.png

  # Streaming with partial images
  python openai_image.py -p "A sunset" --stream --partial-images 2
        """
    )

    parser.add_argument("--prompt", "-p", required=True, help="Image generation/editing prompt")
    parser.add_argument("--model", "-m", default="gpt-image-1",
                        choices=["gpt-image-1.5", "gpt-image-1", "gpt-image-1-mini"],
                        help="Model to use (default: gpt-image-1)")
    parser.add_argument("--size", "-s", default="auto",
                        choices=["1024x1024", "1536x1024", "1024x1536", "auto"],
                        help="Image size (default: auto)")
    parser.add_argument("--quality", "-q", default="auto",
                        choices=["low", "medium", "high", "auto"],
                        help="Quality level (default: auto)")
    parser.add_argument("--background", "-b", default="auto",
                        choices=["transparent", "opaque", "auto"],
                        help="Background type (default: auto)")
    parser.add_argument("--format", "-f", dest="output_format", default="png",
                        choices=["png", "jpeg", "webp"],
                        help="Output format (default: png)")
    parser.add_argument("--compression", "-c", type=int, default=None,
                        help="Compression level 0-100 (for jpeg/webp only)")
    parser.add_argument("--n", type=int, default=1,
                        help="Number of images to generate (1-10, default: 1)")
    parser.add_argument("--moderation", default="auto",
                        choices=["auto", "low"],
                        help="Moderation level (default: auto)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output file path")

    # Image editing options
    parser.add_argument("--image", "-i", action="append", dest="images",
                        help="Input image for editing (can use multiple times, up to 16)")
    parser.add_argument("--mask", default=None,
                        help="Mask image for inpainting")
    parser.add_argument("--input-fidelity", default="low",
                        choices=["low", "high"],
                        help="Input fidelity for preserving details (default: low)")

    # Streaming options
    parser.add_argument("--stream", action="store_true",
                        help="Enable streaming mode")
    parser.add_argument("--partial-images", type=int, default=2,
                        help="Number of partial images during streaming (0-3, default: 2)")

    args = parser.parse_args()

    print(f"OpenAI GPT Image Generation")
    print(f"Model: {args.model}")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")

    # Determine which mode to use
    if args.images:
        # Image editing mode
        print(f"Mode: Image Editing")
        print(f"Input images: {len(args.images)}")
        for img in args.images:
            print(f"  - {img}")
        if args.mask:
            print(f"Mask: {args.mask}")
        print(f"Input fidelity: {args.input_fidelity}")
        print()

        result = edit_image(
            args.prompt,
            args.images,
            args.mask,
            args.model,
            args.size,
            args.quality,
            args.background,
            args.output_format,
            args.compression,
            args.input_fidelity,
            args.n,
            args.output
        )
    elif args.stream:
        # Streaming mode
        print(f"Mode: Streaming Generation")
        print(f"Partial images: {args.partial_images}")
        print()

        result = generate_streaming(
            args.prompt,
            args.model,
            args.size,
            args.quality,
            args.partial_images,
            args.output
        )
    else:
        # Standard generation mode
        print(f"Mode: Text-to-Image Generation")
        print(f"Size: {args.size}, Quality: {args.quality}")
        print(f"Background: {args.background}, Format: {args.output_format}")
        if args.compression is not None:
            print(f"Compression: {args.compression}%")
        print()

        result = generate_image(
            args.prompt,
            args.model,
            args.size,
            args.quality,
            args.background,
            args.output_format,
            args.compression,
            args.n,
            args.moderation,
            args.output
        )

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("Image generated successfully!")
        if "images" in result:
            for img in result["images"]:
                print(f"  Saved to: {img['file']}")
                if img.get("revised_prompt"):
                    print(f"  Revised prompt: {img['revised_prompt'][:100]}...")
        elif "file" in result:
            print(f"  Saved to: {result['file']}")
        print()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
