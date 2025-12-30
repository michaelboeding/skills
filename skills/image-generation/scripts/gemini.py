#!/usr/bin/env python3
"""
Google Gemini Image Generation Script (Imagen 3)
Requires: GOOGLE_API_KEY environment variable
"""

import argparse
import os
import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import base64
from datetime import datetime


def generate_image(prompt: str, aspect_ratio: str = "1:1", 
                   safety_setting: str = "block_medium_and_above") -> dict:
    """Generate an image using Google Gemini API (Imagen 3)."""
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY environment variable not set. Get your key at https://aistudio.google.com/apikey then run: export GOOGLE_API_KEY='your-key'"}
    
    # Gemini API endpoint for image generation
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Map aspect ratio to dimensions
    aspect_ratios = {
        "1:1": {"width": 1024, "height": 1024},
        "16:9": {"width": 1344, "height": 768},
        "9:16": {"width": 768, "height": 1344},
        "4:3": {"width": 1152, "height": 896},
        "3:4": {"width": 896, "height": 1152},
    }
    
    dimensions = aspect_ratios.get(aspect_ratio, aspect_ratios["1:1"])
    
    data = {
        "instances": [
            {"prompt": prompt}
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect_ratio,
            "safetyFilterLevel": safety_setting
        }
    }
    
    try:
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode())
            
            predictions = result.get("predictions", [])
            if not predictions:
                return {"error": "No image generated. Try a different prompt."}
            
            # Get the base64 image
            image_data = predictions[0].get("bytesBase64Encoded")
            if not image_data:
                return {"error": "No image data in response"}
            
            # Save the image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gemini_imagen_{timestamp}.png"
            
            with open(filename, "wb") as f:
                f.write(base64.b64decode(image_data))
            
            return {
                "success": True,
                "file": filename,
                "model": "imagen-3.0-generate-002",
                "aspect_ratio": aspect_ratio,
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


def main():
    parser = argparse.ArgumentParser(description="Generate images using Google Gemini (Imagen 3)")
    parser.add_argument("--prompt", "-p", required=True, help="Image generation prompt")
    parser.add_argument("--aspect-ratio", "-a", default="1:1",
                        choices=["1:1", "16:9", "9:16", "4:3", "3:4"],
                        help="Aspect ratio (default: 1:1)")
    parser.add_argument("--safety", "-s", default="block_medium_and_above",
                        choices=["block_none", "block_low_and_above", "block_medium_and_above", "block_only_high"],
                        help="Safety filter level")
    
    args = parser.parse_args()
    
    print(f"Generating image with Google Gemini (Imagen 3)...")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print(f"Aspect ratio: {args.aspect_ratio}")
    print()
    
    result = generate_image(args.prompt, args.aspect_ratio, args.safety)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Image generated successfully!")
        print(f"Saved to: {result['file']}")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
