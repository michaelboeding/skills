#!/usr/bin/env python3
"""
Google Veo 3 Video Generation Script
Requires: GOOGLE_API_KEY environment variable
"""

import argparse
import os
import sys
import json
from urllib.request import Request, urlopen, urlretrieve
from urllib.error import HTTPError
from datetime import datetime
import time
import base64
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


def generate_video(prompt: str, duration: int = 8, aspect_ratio: str = "16:9") -> dict:
    """Generate a video using Google Veo 3 API."""
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY environment variable not set. Get your key at https://aistudio.google.com/apikey then run: export GOOGLE_API_KEY='your-key'"}
    
    # Validate parameters
    if duration < 1 or duration > 8:
        return {"error": "Duration must be between 1 and 8 seconds"}
    
    valid_aspect_ratios = ["16:9", "9:16", "1:1"]
    if aspect_ratio not in valid_aspect_ratios:
        return {"error": f"Invalid aspect ratio. Must be one of: {valid_aspect_ratios}"}
    
    # Veo 3 API endpoint via Vertex AI / Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/veo-002:generateVideo?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": prompt,
        "generationConfig": {
            "videoDuration": f"{duration}s",
            "aspectRatio": aspect_ratio,
            "numberOfVideos": 1
        }
    }
    
    try:
        # Create generation request
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
        
        # Check for operation/job ID
        operation_name = result.get("name") or result.get("operationId")
        
        if operation_name:
            # Poll for completion
            poll_url = f"https://generativelanguage.googleapis.com/v1beta/{operation_name}?key={api_key}"
            print("Generating video... This may take a few minutes.")
            
            max_attempts = 120
            for attempt in range(max_attempts):
                poll_request = Request(poll_url, headers=headers)
                with urlopen(poll_request, timeout=30) as response:
                    status = json.loads(response.read().decode())
                
                if status.get("done"):
                    if "error" in status:
                        return {"error": f"Generation failed: {status['error']}"}
                    
                    # Extract video from response
                    video_response = status.get("response", {})
                    videos = video_response.get("generatedVideos", [])
                    
                    if not videos:
                        return {"error": "No videos generated"}
                    
                    video_data = videos[0]
                    video_uri = video_data.get("uri") or video_data.get("video", {}).get("uri")
                    
                    # Download or decode video
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"veo3_{timestamp}.mp4"
                    
                    if video_uri:
                        print(f"Downloading video to {filename}...")
                        urlretrieve(video_uri, filename)
                    elif "bytesBase64Encoded" in video_data.get("video", {}):
                        print(f"Saving video to {filename}...")
                        video_bytes = base64.b64decode(video_data["video"]["bytesBase64Encoded"])
                        with open(filename, "wb") as f:
                            f.write(video_bytes)
                    else:
                        return {"error": "No video data in response"}
                    
                    return {
                        "success": True,
                        "file": filename,
                        "duration": duration,
                        "aspect_ratio": aspect_ratio,
                        "model": "veo-3",
                        "prompt": prompt
                    }
                
                if attempt % 10 == 0:
                    print(f"Still generating... ({attempt * 5}s elapsed)")
                time.sleep(5)
            
            return {"error": "Generation timed out after 10 minutes"}
        
        else:
            # Synchronous response (if available)
            videos = result.get("generatedVideos", [])
            if videos:
                video_data = videos[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"veo3_{timestamp}.mp4"
                
                if "bytesBase64Encoded" in video_data.get("video", {}):
                    video_bytes = base64.b64decode(video_data["video"]["bytesBase64Encoded"])
                    with open(filename, "wb") as f:
                        f.write(video_bytes)
                    
                    return {
                        "success": True,
                        "file": filename,
                        "duration": duration,
                        "aspect_ratio": aspect_ratio,
                        "model": "veo-3",
                        "prompt": prompt
                    }
            
            return {"error": f"Unexpected response format: {json.dumps(result)[:200]}"}
            
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
    parser = argparse.ArgumentParser(description="Generate videos using Google Veo 3")
    parser.add_argument("--prompt", "-p", required=True, help="Video generation prompt")
    parser.add_argument("--duration", "-d", type=int, default=8,
                        help="Video duration in seconds 1-8 (default: 8)")
    parser.add_argument("--aspect-ratio", "-a", default="16:9",
                        choices=["16:9", "9:16", "1:1"],
                        help="Aspect ratio (default: 16:9)")
    
    args = parser.parse_args()
    
    print(f"🎬 Generating video with Google Veo 3...")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print(f"Duration: {args.duration}s, Aspect ratio: {args.aspect_ratio}")
    print()
    
    result = generate_video(args.prompt, args.duration, args.aspect_ratio)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Video generated successfully!")
        print(f"Saved to: {result['file']}")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
