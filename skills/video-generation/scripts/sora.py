#!/usr/bin/env python3
"""
OpenAI Sora Video Generation Script
Requires: OPENAI_API_KEY environment variable
"""

import argparse
import os
import sys
import json
from urllib.request import Request, urlopen, urlretrieve
from urllib.error import HTTPError
from datetime import datetime
import time
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


def generate_video(prompt: str, duration: int = 10, resolution: str = "1080p",
                   aspect_ratio: str = "16:9", style: str = "natural") -> dict:
    """Generate a video using OpenAI Sora API."""
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY environment variable not set. Get your key at https://platform.openai.com/api-keys then run: export OPENAI_API_KEY='sk-...'"}
    
    # Validate parameters
    valid_durations = [5, 10, 15, 20]
    valid_resolutions = ["480p", "720p", "1080p"]
    valid_aspect_ratios = ["16:9", "9:16", "1:1"]
    
    if duration not in valid_durations:
        return {"error": f"Invalid duration. Must be one of: {valid_durations}"}
    if resolution not in valid_resolutions:
        return {"error": f"Invalid resolution. Must be one of: {valid_resolutions}"}
    if aspect_ratio not in valid_aspect_ratios:
        return {"error": f"Invalid aspect ratio. Must be one of: {valid_aspect_ratios}"}
    
    # Sora API endpoint
    url = "https://api.openai.com/v1/videos/generations"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Map resolution to dimensions
    resolution_map = {
        "480p": {"width": 854, "height": 480},
        "720p": {"width": 1280, "height": 720},
        "1080p": {"width": 1920, "height": 1080}
    }
    
    # Adjust for aspect ratio
    dims = resolution_map[resolution]
    if aspect_ratio == "9:16":
        dims = {"width": dims["height"], "height": dims["width"]}
    elif aspect_ratio == "1:1":
        size = min(dims["width"], dims["height"])
        dims = {"width": size, "height": size}
    
    data = {
        "model": "sora",
        "prompt": prompt,
        "duration": duration,
        "resolution": f"{dims['width']}x{dims['height']}",
        "aspect_ratio": aspect_ratio,
        "style": style
    }
    
    try:
        # Create generation request
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
        
        # Get the generation ID for polling
        generation_id = result.get("id")
        if not generation_id:
            return {"error": "No generation ID returned"}
        
        # Poll for completion
        poll_url = f"https://api.openai.com/v1/videos/generations/{generation_id}"
        print("Generating video... This may take a few minutes.")
        
        max_attempts = 120  # Up to 10 minutes
        for attempt in range(max_attempts):
            poll_request = Request(poll_url, headers=headers)
            with urlopen(poll_request, timeout=30) as response:
                status = json.loads(response.read().decode())
            
            if status["status"] == "completed":
                video_url = status.get("video_url") or status.get("output", {}).get("url")
                
                if not video_url:
                    return {"error": "No video URL in response"}
                
                # Download the video
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"sora_{timestamp}.mp4"
                
                print(f"Downloading video to {filename}...")
                urlretrieve(video_url, filename)
                
                return {
                    "success": True,
                    "file": filename,
                    "url": video_url,
                    "duration": duration,
                    "resolution": resolution,
                    "aspect_ratio": aspect_ratio,
                    "model": "sora",
                    "prompt": prompt
                }
            
            elif status["status"] == "failed":
                return {"error": f"Generation failed: {status.get('error', 'Unknown error')}"}
            
            elif status["status"] == "cancelled":
                return {"error": "Generation was cancelled"}
            
            # Still processing
            if attempt % 10 == 0:
                print(f"Still generating... ({attempt * 5}s elapsed)")
            time.sleep(5)
        
        return {"error": "Generation timed out after 10 minutes"}
            
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
    parser = argparse.ArgumentParser(description="Generate videos using OpenAI Sora")
    parser.add_argument("--prompt", "-p", required=True, help="Video generation prompt")
    parser.add_argument("--duration", "-d", type=int, default=10,
                        choices=[5, 10, 15, 20],
                        help="Video duration in seconds (default: 10)")
    parser.add_argument("--resolution", "-r", default="1080p",
                        choices=["480p", "720p", "1080p"],
                        help="Video resolution (default: 1080p)")
    parser.add_argument("--aspect-ratio", "-a", default="16:9",
                        choices=["16:9", "9:16", "1:1"],
                        help="Aspect ratio (default: 16:9)")
    parser.add_argument("--style", "-s", default="natural",
                        choices=["natural", "vivid"],
                        help="Video style (default: natural)")
    
    args = parser.parse_args()
    
    print(f"🎬 Generating video with OpenAI Sora...")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print(f"Duration: {args.duration}s, Resolution: {args.resolution}, Aspect: {args.aspect_ratio}")
    print()
    
    result = generate_video(args.prompt, args.duration, args.resolution, 
                           args.aspect_ratio, args.style)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Video generated successfully!")
        print(f"Saved to: {result['file']}")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
