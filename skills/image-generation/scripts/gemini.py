#!/usr/bin/env python3
"""
Google Gemini Native Image Generation Script (Nano Banana / Nano Banana Pro)
Requires: GOOGLE_API_KEY environment variable

Models:
- gemini-2.5-flash-image (Nano Banana) - Fast, efficient, 1K resolution, up to 3 reference images
- gemini-3-pro-image-preview (Nano Banana Pro) - Professional, up to 4K, thinking mode, up to 14 reference images

Supports:
- Text-to-image generation
- Image editing with reference images
- Style transfer
- Product placement
- Multi-image composition
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


def load_env():
    """Load environment variables from .env file in repo root."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        env_file = current / ".env"
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
            return
        current = current.parent


load_env()


def load_image_as_base64(image_path: str) -> tuple:
    """Load an image file and return base64 data and mime type."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Determine mime type
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


def generate_image(prompt: str, model: str = "gemini-3-pro-image-preview",
                   aspect_ratio: str = "1:1", resolution: str = "1K",
                   reference_images: list = None) -> dict:
    """Generate an image using Google Gemini native image generation.
    
    Args:
        prompt: Text prompt for image generation or editing
        model: Model to use (gemini-2.5-flash-image or gemini-3-pro-image-preview)
        aspect_ratio: Output aspect ratio
        resolution: Output resolution (1K, 2K, 4K) - Pro only
        reference_images: List of image file paths to use as references
    """
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY environment variable not set. Get your key at https://aistudio.google.com/apikey"}
    
    # Validate model
    valid_models = ["gemini-2.5-flash-image", "gemini-3-pro-image-preview"]
    if model not in valid_models:
        return {"error": f"Invalid model. Must be one of: {valid_models}"}
    
    # Validate aspect ratio
    valid_ratios = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
    if aspect_ratio not in valid_ratios:
        return {"error": f"Invalid aspect ratio. Must be one of: {valid_ratios}"}
    
    # Validate resolution (only for Nano Banana Pro)
    valid_resolutions = ["1K", "2K", "4K"]
    if resolution not in valid_resolutions:
        return {"error": f"Invalid resolution. Must be one of: {valid_resolutions}"}
    
    # Validate reference image count
    if reference_images:
        max_images = 14 if model == "gemini-3-pro-image-preview" else 3
        if len(reference_images) > max_images:
            return {"error": f"Too many reference images. {model} supports up to {max_images} images."}
    
    # Gemini API endpoint for native image generation
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Build the content parts
    parts = []
    
    # Add text prompt
    parts.append({"text": prompt})
    
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
                return {"error": f"Failed to load image {img_path}: {str(e)}"}
    
    # Build the request payload
    data = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"]
        }
    }
    
    # Add image config for aspect ratio and resolution
    image_config = {"aspectRatio": aspect_ratio}
    
    # Resolution is only supported by Nano Banana Pro
    if model == "gemini-3-pro-image-preview":
        image_config["imageSize"] = resolution
    
    data["generationConfig"]["imageConfig"] = image_config
    
    try:
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=300) as response:  # Longer timeout for image processing
            result = json.loads(response.read().decode())
            
            candidates = result.get("candidates", [])
            if not candidates:
                return {"error": "No response generated. Try a different prompt."}
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                return {"error": "No content in response"}
            
            # Extract image and text from response
            image_data = None
            response_text = None
            
            for part in parts:
                # Skip thought parts (interim images during thinking)
                if part.get("thought"):
                    continue
                    
                if "inlineData" in part:
                    image_data = part["inlineData"].get("data")
                elif "text" in part:
                    response_text = part["text"]
            
            if not image_data:
                return {"error": "No image data in response. The model may have returned text only."}
            
            # Save the image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gemini_{model.split('-')[1]}_{timestamp}.png"
            
            with open(filename, "wb") as f:
                f.write(base64.b64decode(image_data))
            
            result_data = {
                "success": True,
                "file": filename,
                "model": model,
                "aspect_ratio": aspect_ratio,
                "prompt": prompt
            }
            
            if model == "gemini-3-pro-image-preview":
                result_data["resolution"] = resolution
            
            if reference_images:
                result_data["reference_images"] = reference_images
            
            if response_text:
                result_data["model_response"] = response_text
            
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
        description="Generate images using Google Gemini (Nano Banana / Nano Banana Pro)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Models:
  gemini-2.5-flash-image      Nano Banana - Fast, 1K, up to 3 reference images
  gemini-3-pro-image-preview  Nano Banana Pro - Professional, up to 4K, up to 14 reference images

Examples:
  # Text-to-image
  python gemini.py -p "A cat wearing a space helmet" -a 1:1 -r 2K

  # Image editing - add element
  python gemini.py -p "Add a wizard hat to this cat" --image cat.jpg

  # Product placement
  python gemini.py -p "Place this product on a kitchen counter" --image product.png --image kitchen.jpg

  # Style transfer
  python gemini.py -p "Transform this photo into Van Gogh style" --image photo.jpg

  # Multi-image composition
  python gemini.py -p "Create a group photo of these people" --image person1.jpg --image person2.jpg --image person3.jpg
        """
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image generation or editing prompt")
    parser.add_argument("--model", "-m", default="gemini-3-pro-image-preview",
                        choices=["gemini-2.5-flash-image", "gemini-3-pro-image-preview"],
                        help="Model to use (default: gemini-3-pro-image-preview / Nano Banana Pro)")
    parser.add_argument("--aspect-ratio", "-a", default="1:1",
                        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
                        help="Aspect ratio (default: 1:1)")
    parser.add_argument("--resolution", "-r", default="1K",
                        choices=["1K", "2K", "4K"],
                        help="Resolution - only for Nano Banana Pro (default: 1K)")
    parser.add_argument("--image", "-i", action="append", dest="images",
                        help="Reference image path (can be used multiple times for multiple images)")
    
    args = parser.parse_args()
    
    model_name = "Nano Banana Pro" if args.model == "gemini-3-pro-image-preview" else "Nano Banana"
    
    print(f"🎨 Generating image with Google Gemini ({model_name})...")
    print(f"Model: {args.model}")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print(f"Aspect ratio: {args.aspect_ratio}")
    if args.model == "gemini-3-pro-image-preview":
        print(f"Resolution: {args.resolution}")
    if args.images:
        print(f"Reference images: {len(args.images)}")
        for img in args.images:
            print(f"  - {img}")
    print()
    
    result = generate_image(
        args.prompt, 
        args.model, 
        args.aspect_ratio, 
        args.resolution,
        args.images
    )
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Image generated successfully!")
        print(f"Saved to: {result['file']}")
        if result.get("model_response"):
            print(f"Model response: {result['model_response'][:200]}...")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
