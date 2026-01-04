#!/usr/bin/env python3
"""
Udio Music Generation Script
Requires: UDIO_API_KEY environment variable
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


def generate_music(prompt: str, duration: int = 120, quality: str = "high") -> dict:
    """Generate music using Udio API."""
    
    api_key = os.environ.get("UDIO_API_KEY")
    if not api_key:
        return {"error": "UDIO_API_KEY environment variable not set. Get your key at https://udio.com then run: export UDIO_API_KEY='your-key'"}
    
    # Validate parameters
    if duration < 30 or duration > 120:
        return {"error": "Duration must be between 30 and 120 seconds"}
    
    valid_qualities = ["standard", "high"]
    if quality not in valid_qualities:
        return {"error": f"Invalid quality. Must be one of: {valid_qualities}"}
    
    # Udio API endpoint
    url = "https://api.udio.com/v1/generations"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "prompt": prompt,
        "duration_seconds": duration,
        "quality": quality
    }
    
    try:
        # Create generation request
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
        
        # Get generation ID
        gen_id = result.get("id") or result.get("generation_id")
        
        if not gen_id:
            # Check if audio is immediately available
            if "audio_url" in result:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"udio_{timestamp}.mp3"
                urlretrieve(result["audio_url"], filename)
                return {
                    "success": True,
                    "file": filename,
                    "url": result["audio_url"],
                    "duration": duration,
                    "quality": quality,
                    "model": "udio",
                    "prompt": prompt
                }
            return {"error": "No generation ID returned"}
        
        # Poll for completion
        poll_url = f"https://api.udio.com/v1/generations/{gen_id}"
        print("Generating music... This may take a minute or two.")
        
        max_attempts = 60  # Up to 5 minutes
        for attempt in range(max_attempts):
            poll_request = Request(poll_url, headers=headers)
            with urlopen(poll_request, timeout=30) as response:
                status = json.loads(response.read().decode())
            
            gen_status = status.get("status", "").lower()
            
            if gen_status in ["complete", "completed", "succeeded"]:
                audio_url = status.get("audio_url") or status.get("output", {}).get("url")
                
                if not audio_url:
                    return {"error": "No audio URL in response"}
                
                # Download the audio
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"udio_{timestamp}.mp3"
                
                print(f"Downloading audio to {filename}...")
                urlretrieve(audio_url, filename)
                
                return {
                    "success": True,
                    "file": filename,
                    "url": audio_url,
                    "duration": status.get("duration", duration),
                    "quality": quality,
                    "model": "udio",
                    "prompt": prompt
                }
            
            elif gen_status in ["failed", "error"]:
                return {"error": f"Generation failed: {status.get('error', 'Unknown error')}"}
            
            elif gen_status == "cancelled":
                return {"error": "Generation was cancelled"}
            
            # Still processing
            if attempt % 6 == 0:
                print(f"Still generating... ({attempt * 5}s elapsed)")
            time.sleep(5)
        
        return {"error": "Generation timed out after 5 minutes"}
            
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
    parser = argparse.ArgumentParser(description="Generate music using Udio")
    parser.add_argument("--prompt", "-p", required=True,
                        help="Music style/genre prompt")
    parser.add_argument("--duration", "-d", type=int, default=120,
                        help="Duration in seconds 30-120 (default: 120)")
    parser.add_argument("--quality", "-q", default="high",
                        choices=["standard", "high"],
                        help="Audio quality (default: high)")
    
    args = parser.parse_args()
    
    print(f"🎵 Generating music with Udio...")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print(f"Duration: {args.duration}s, Quality: {args.quality}")
    print()
    
    result = generate_music(args.prompt, args.duration, args.quality)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Music generated successfully!")
        print(f"Saved to: {result['file']}")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
