#!/usr/bin/env python3
"""
ElevenLabs Text-to-Speech Script
Requires: ELEVENLABS_API_KEY environment variable
"""

import argparse
import os
import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime
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


# Popular ElevenLabs voice IDs
VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "domi": "AZnzlk1XvdvUeBnXmlld",
    "bella": "EXAVITQu4vr4xnSDxMaL",
    "antoni": "ErXwobaYiN019PkySvjV",
    "elli": "MF3mGyEYCl7XYWbV9V6O",
    "josh": "TxGEqnHWrfWFTfGW9XjX",
    "arnold": "VR6AewLTigWG4xSOukaG",
    "adam": "pNInz6obpgDQGcFmaJgB",
    "sam": "yoZ06aMxZJJ28mfd3POQ",
}

MODELS = {
    "eleven_multilingual_v2": "eleven_multilingual_v2",
    "eleven_turbo_v2": "eleven_turbo_v2",
    "eleven_monolingual_v1": "eleven_monolingual_v1",
}


def get_voices(api_key: str) -> dict:
    """Fetch available voices from ElevenLabs API."""
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    
    try:
        request = Request(url, headers=headers)
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
            return {v["name"].lower(): v["voice_id"] for v in result.get("voices", [])}
    except:
        return VOICES


def generate_speech(text: str, voice: str = "rachel", model: str = "eleven_multilingual_v2",
                    stability: float = 0.5, similarity_boost: float = 0.75,
                    output_format: str = "mp3_44100_128") -> dict:
    """Generate speech using ElevenLabs API."""
    
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        return {"error": "ELEVENLABS_API_KEY environment variable not set. Get your key at https://elevenlabs.io then run: export ELEVENLABS_API_KEY='your-key'"}
    
    # Get voice ID
    voice_lower = voice.lower()
    if voice_lower in VOICES:
        voice_id = VOICES[voice_lower]
    elif len(voice) == 21:  # Looks like a voice ID
        voice_id = voice
    else:
        # Try to fetch from API
        all_voices = get_voices(api_key)
        voice_id = all_voices.get(voice_lower, VOICES.get("rachel"))
    
    # Get model ID
    model_id = MODELS.get(model, model)
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    
    data = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }
    
    try:
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=120) as response:
            audio_data = response.read()
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"elevenlabs_{voice}_{timestamp}.mp3"
            
            with open(filename, "wb") as f:
                f.write(audio_data)
            
            return {
                "success": True,
                "file": filename,
                "voice": voice,
                "voice_id": voice_id,
                "model": model_id,
                "characters": len(text),
                "size_bytes": len(audio_data)
            }
            
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        try:
            error_json = json.loads(error_body)
            error_message = error_json.get("detail", {}).get("message", error_body)
        except:
            error_message = error_body
        return {"error": f"API error ({e.code}): {error_message}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def list_voices():
    """List available voices."""
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if api_key:
        voices = get_voices(api_key)
        print("Available voices:")
        for name, voice_id in sorted(voices.items()):
            print(f"  {name}: {voice_id}")
    else:
        print("Default voices (set ELEVENLABS_API_KEY for full list):")
        for name, voice_id in VOICES.items():
            print(f"  {name}: {voice_id}")


def main():
    parser = argparse.ArgumentParser(description="Generate speech using ElevenLabs")
    parser.add_argument("--text", "-t", help="Text to convert to speech")
    parser.add_argument("--voice", "-v", default="rachel",
                        help="Voice name or ID (default: rachel)")
    parser.add_argument("--model", "-m", default="eleven_multilingual_v2",
                        choices=list(MODELS.keys()),
                        help="Model to use (default: eleven_multilingual_v2)")
    parser.add_argument("--stability", "-s", type=float, default=0.5,
                        help="Voice stability 0-1 (default: 0.5)")
    parser.add_argument("--similarity", type=float, default=0.75,
                        help="Similarity boost 0-1 (default: 0.75)")
    parser.add_argument("--list-voices", "-l", action="store_true",
                        help="List available voices")
    parser.add_argument("--file", "-f", help="Read text from file")
    
    args = parser.parse_args()
    
    if args.list_voices:
        list_voices()
        return
    
    # Get text from argument or file
    if args.file:
        with open(args.file, "r") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        parser.error("Either --text or --file is required")
        return
    
    print(f"Generating speech with ElevenLabs...")
    print(f"Voice: {args.voice}, Model: {args.model}")
    print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
    print()
    
    result = generate_speech(text, args.voice, args.model, args.stability, args.similarity)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Audio generated successfully!")
        print(f"Saved to: {result['file']}")
        print(f"Characters: {result['characters']}, Size: {result['size_bytes']} bytes")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
