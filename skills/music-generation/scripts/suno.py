#!/usr/bin/env python3
"""
Suno Music Generation Script
Requires: SUNO_API_KEY environment variable
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


def generate_music(prompt: str, title: str = None, lyrics: str = None,
                   instrumental: bool = False, duration: int = 120) -> dict:
    """Generate music using Suno API."""
    
    api_key = os.environ.get("SUNO_API_KEY")
    if not api_key:
        return {"error": "SUNO_API_KEY environment variable not set. Get your key at https://suno.com then run: export SUNO_API_KEY='your-key'"}
    
    # Suno API endpoint (unofficial/community API - adjust as needed)
    url = "https://api.suno.ai/v1/generations"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "prompt": prompt,
        "make_instrumental": instrumental,
        "wait_audio": False  # Use async polling
    }
    
    if title:
        data["title"] = title
    
    if lyrics and not instrumental:
        data["lyrics"] = lyrics
    
    try:
        # Create generation request
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
        
        # Get generation ID(s)
        generations = result if isinstance(result, list) else [result]
        
        if not generations:
            return {"error": "No generation created"}
        
        gen_id = generations[0].get("id")
        if not gen_id:
            return {"error": "No generation ID returned"}
        
        # Poll for completion
        poll_url = f"https://api.suno.ai/v1/generations/{gen_id}"
        print("Generating music... This may take a minute or two.")
        
        max_attempts = 60  # Up to 5 minutes
        for attempt in range(max_attempts):
            poll_request = Request(poll_url, headers=headers)
            with urlopen(poll_request, timeout=30) as response:
                status = json.loads(response.read().decode())
            
            if status.get("status") == "complete":
                audio_url = status.get("audio_url")
                
                if not audio_url:
                    return {"error": "No audio URL in response"}
                
                # Download the audio
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = (title or "suno").replace(" ", "_")[:20]
                filename = f"{safe_title}_{timestamp}.mp3"
                
                print(f"Downloading audio to {filename}...")
                urlretrieve(audio_url, filename)
                
                return {
                    "success": True,
                    "file": filename,
                    "url": audio_url,
                    "title": status.get("title", title),
                    "duration": status.get("duration"),
                    "model": "suno",
                    "instrumental": instrumental,
                    "prompt": prompt
                }
            
            elif status.get("status") == "failed":
                return {"error": f"Generation failed: {status.get('error', 'Unknown error')}"}
            
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
    parser = argparse.ArgumentParser(description="Generate music using Suno")
    parser.add_argument("--prompt", "-p", required=True, 
                        help="Music style/genre prompt (e.g., 'upbeat pop, summer vibes')")
    parser.add_argument("--title", "-t", 
                        help="Song title")
    parser.add_argument("--lyrics", "-l",
                        help="Custom lyrics (or path to lyrics file)")
    parser.add_argument("--instrumental", "-i", action="store_true",
                        help="Generate instrumental only (no vocals)")
    parser.add_argument("--lyrics-file", "-f",
                        help="Path to file containing lyrics")
    
    args = parser.parse_args()
    
    # Load lyrics from file if provided
    lyrics = args.lyrics
    if args.lyrics_file:
        try:
            with open(args.lyrics_file, "r") as f:
                lyrics = f.read()
        except Exception as e:
            print(f"Error reading lyrics file: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(f"🎵 Generating music with Suno...")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    if args.title:
        print(f"Title: {args.title}")
    print(f"Mode: {'Instrumental' if args.instrumental else 'With vocals'}")
    print()
    
    result = generate_music(args.prompt, args.title, lyrics, args.instrumental)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Music generated successfully!")
        print(f"Saved to: {result['file']}")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
