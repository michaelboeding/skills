#!/usr/bin/env python3
"""
OpenAI Text-to-Speech Script
Requires: OPENAI_API_KEY environment variable
"""

import argparse
import os
import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime


VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
MODELS = ["tts-1", "tts-1-hd"]
FORMATS = ["mp3", "opus", "aac", "flac"]


def generate_speech(text: str, voice: str = "nova", model: str = "tts-1",
                    speed: float = 1.0, response_format: str = "mp3") -> dict:
    """Generate speech using OpenAI TTS API."""
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY environment variable not set. Get your key at https://platform.openai.com/api-keys"}
    
    # Validate parameters
    if voice not in VOICES:
        return {"error": f"Invalid voice. Must be one of: {VOICES}"}
    if model not in MODELS:
        return {"error": f"Invalid model. Must be one of: {MODELS}"}
    if response_format not in FORMATS:
        return {"error": f"Invalid format. Must be one of: {FORMATS}"}
    if not 0.25 <= speed <= 4.0:
        return {"error": "Speed must be between 0.25 and 4.0"}
    
    # Check text length (max 4096 characters)
    if len(text) > 4096:
        return {"error": f"Text too long ({len(text)} chars). Maximum is 4096 characters."}
    
    url = "https://api.openai.com/v1/audio/speech"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "input": text,
        "voice": voice,
        "speed": speed,
        "response_format": response_format
    }
    
    try:
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=120) as response:
            audio_data = response.read()
            
            # Determine file extension
            ext = response_format if response_format != "opus" else "ogg"
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"openai_tts_{voice}_{timestamp}.{ext}"
            
            with open(filename, "wb") as f:
                f.write(audio_data)
            
            return {
                "success": True,
                "file": filename,
                "voice": voice,
                "model": model,
                "speed": speed,
                "format": response_format,
                "characters": len(text),
                "size_bytes": len(audio_data)
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
    parser = argparse.ArgumentParser(description="Generate speech using OpenAI TTS")
    parser.add_argument("--text", "-t", help="Text to convert to speech")
    parser.add_argument("--voice", "-v", default="nova",
                        choices=VOICES,
                        help="Voice to use (default: nova)")
    parser.add_argument("--model", "-m", default="tts-1",
                        choices=MODELS,
                        help="Model: tts-1 (fast) or tts-1-hd (quality)")
    parser.add_argument("--speed", "-s", type=float, default=1.0,
                        help="Speed 0.25-4.0 (default: 1.0)")
    parser.add_argument("--format", "-f", default="mp3",
                        choices=FORMATS,
                        help="Output format (default: mp3)")
    parser.add_argument("--file", help="Read text from file")
    
    args = parser.parse_args()
    
    # Get text from argument or file
    if args.file:
        with open(args.file, "r") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        parser.error("Either --text or --file is required")
        return
    
    print(f"Generating speech with OpenAI TTS...")
    print(f"Voice: {args.voice}, Model: {args.model}, Speed: {args.speed}x")
    print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
    print()
    
    result = generate_speech(text, args.voice, args.model, args.speed, args.format)
    
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
