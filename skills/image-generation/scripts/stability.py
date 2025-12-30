#!/usr/bin/env python3
"""
Stability AI Image Generation Script
Requires: STABILITY_API_KEY environment variable
"""

import argparse
import os
import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import base64
from datetime import datetime


def generate_image(prompt: str, width: int = 1024, height: int = 1024, 
                   negative_prompt: str = "", seed: int = 0) -> dict:
    """Generate an image using Stability AI API."""
    
    api_key = os.environ.get("STABILITY_API_KEY")
    if not api_key:
        return {"error": "STABILITY_API_KEY environment variable not set. Get your key at https://platform.stability.ai/account/keys then run: export STABILITY_API_KEY='sk-...'"}
    
    # Use Stable Diffusion 3
    url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    # Build multipart form data manually
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    def add_field(name, value):
        return f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'
    
    body = ""
    body += add_field("prompt", prompt)
    body += add_field("output_format", "png")
    body += add_field("aspect_ratio", get_aspect_ratio(width, height))
    
    if negative_prompt:
        body += add_field("negative_prompt", negative_prompt)
    if seed > 0:
        body += add_field("seed", str(seed))
    
    body += f"--{boundary}--\r\n"
    
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    
    try:
        request = Request(url, data=body.encode(), headers=headers, method="POST")
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode())
            
            # Save the image
            if "image" in result:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stability_{timestamp}.png"
                
                image_data = base64.b64decode(result["image"])
                with open(filename, "wb") as f:
                    f.write(image_data)
                
                return {
                    "success": True,
                    "file": filename,
                    "seed": result.get("seed", seed),
                    "model": "stable-diffusion-3",
                    "prompt": prompt
                }
            else:
                return {"error": "No image in response"}
            
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        try:
            error_json = json.loads(error_body)
            error_message = error_json.get("message", error_body)
        except:
            error_message = error_body
        return {"error": f"API error ({e.code}): {error_message}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def get_aspect_ratio(width: int, height: int) -> str:
    """Convert width/height to Stability AI aspect ratio string."""
    ratio = width / height
    
    # Map to supported aspect ratios
    ratios = {
        1.0: "1:1",
        16/9: "16:9",
        9/16: "9:16",
        21/9: "21:9",
        9/21: "9:21",
        4/3: "4:3",
        3/4: "3:4",
        3/2: "3:2",
        2/3: "2:3",
        5/4: "5:4",
        4/5: "4:5"
    }
    
    # Find closest match
    closest = min(ratios.keys(), key=lambda x: abs(x - ratio))
    return ratios[closest]


def main():
    parser = argparse.ArgumentParser(description="Generate images using Stability AI")
    parser.add_argument("--prompt", "-p", required=True, help="Image generation prompt")
    parser.add_argument("--width", "-W", type=int, default=1024, help="Image width (default: 1024)")
    parser.add_argument("--height", "-H", type=int, default=1024, help="Image height (default: 1024)")
    parser.add_argument("--negative", "-n", default="", help="Negative prompt (what to avoid)")
    parser.add_argument("--seed", "-s", type=int, default=0, help="Seed for reproducibility")
    
    args = parser.parse_args()
    
    print(f"Generating image with Stability AI...")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print(f"Size: {args.width}x{args.height}")
    print()
    
    result = generate_image(args.prompt, args.width, args.height, args.negative, args.seed)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Image generated successfully!")
        print(f"Saved to: {result['file']}")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
