#!/usr/bin/env python3
"""
DALL-E 3 Image Generation Script
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


def generate_image(prompt: str, size: str = "1024x1024", style: str = "vivid", quality: str = "standard") -> dict:
    """Generate an image using DALL-E 3 API."""
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY environment variable not set. Please set it in your shell or .env file."}
    
    # Validate parameters
    valid_sizes = ["1024x1024", "1024x1792", "1792x1024"]
    valid_styles = ["vivid", "natural"]
    valid_qualities = ["standard", "hd"]
    
    if size not in valid_sizes:
        return {"error": f"Invalid size. Must be one of: {valid_sizes}"}
    if style not in valid_styles:
        return {"error": f"Invalid style. Must be one of: {valid_styles}"}
    if quality not in valid_qualities:
        return {"error": f"Invalid quality. Must be one of: {valid_qualities}"}
    
    # Prepare request
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "style": style,
        "quality": quality,
        "response_format": "url"
    }
    
    try:
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode())
            
            image_url = result["data"][0]["url"]
            revised_prompt = result["data"][0].get("revised_prompt", prompt)
            
            return {
                "success": True,
                "url": image_url,
                "revised_prompt": revised_prompt,
                "model": "dall-e-3",
                "size": size,
                "style": style,
                "quality": quality
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
    parser = argparse.ArgumentParser(description="Generate images using DALL-E 3")
    parser.add_argument("--prompt", "-p", required=True, help="Image generation prompt")
    parser.add_argument("--size", "-s", default="1024x1024", 
                        choices=["1024x1024", "1024x1792", "1792x1024"],
                        help="Image size (default: 1024x1024)")
    parser.add_argument("--style", default="vivid",
                        choices=["vivid", "natural"],
                        help="Image style: vivid (dramatic) or natural (realistic)")
    parser.add_argument("--quality", "-q", default="standard",
                        choices=["standard", "hd"],
                        help="Image quality (default: standard)")
    
    args = parser.parse_args()
    
    print(f"Generating image with DALL-E 3...")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print(f"Size: {args.size}, Style: {args.style}, Quality: {args.quality}")
    print()
    
    result = generate_image(args.prompt, args.size, args.style, args.quality)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Image generated successfully!")
        print(f"URL: {result['url']}")
        print(f"Revised prompt: {result['revised_prompt']}")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
