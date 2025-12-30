#!/usr/bin/env python3
"""
Replicate Text-to-Speech Script
Requires: REPLICATE_API_TOKEN environment variable
"""

import argparse
import os
import sys
import json
from urllib.request import Request, urlopen, urlretrieve
from urllib.error import HTTPError
from datetime import datetime
import time


# Popular TTS models on Replicate
MODELS = {
    "coqui-xtts": "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
    "bark": "suno-ai/bark:b76242b40d67c76ab6742e987628a2a9ac019e11d56ab96c4e91ce03b79b2787",
    "tortoise": "afiaka87/tortoise-tts:e9658de4b325863c4fcdc12d94bb7c9b54cbfe351b7ca1b36860008172b91c71",
}


def generate_speech(text: str, model: str = "coqui-xtts", 
                    language: str = "en", speaker_url: str = None) -> dict:
    """Generate speech using Replicate API."""
    
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not api_token:
        return {"error": "REPLICATE_API_TOKEN environment variable not set. Get your token at https://replicate.com/account/api-tokens"}
    
    # Get model version
    model_version = MODELS.get(model, model)
    
    if ":" not in model_version:
        return {"error": f"Unknown model '{model}'. Available: {list(MODELS.keys())}"}
    
    version = model_version.split(":")[1]
    
    url = "https://api.replicate.com/v1/predictions"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Build input based on model
    if "xtts" in model.lower():
        input_data = {
            "text": text,
            "language": language,
        }
        if speaker_url:
            input_data["speaker"] = speaker_url
    elif "bark" in model.lower():
        input_data = {
            "prompt": text,
            "text_temp": 0.7,
            "waveform_temp": 0.7,
        }
    elif "tortoise" in model.lower():
        input_data = {
            "text": text,
            "voice_a": "random",
            "preset": "fast",
        }
    else:
        input_data = {"text": text}
    
    data = {
        "version": version,
        "input": input_data
    }
    
    try:
        # Create prediction
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
        
        prediction_url = result.get("urls", {}).get("get", f"https://api.replicate.com/v1/predictions/{result['id']}")
        
        # Poll for completion
        print("Waiting for generation to complete...")
        max_attempts = 120  # TTS can take a while
        for attempt in range(max_attempts):
            poll_request = Request(prediction_url, headers=headers)
            with urlopen(poll_request, timeout=30) as response:
                status = json.loads(response.read().decode())
            
            if status["status"] == "succeeded":
                output = status.get("output")
                
                # Handle different output formats
                if isinstance(output, str):
                    audio_url = output
                elif isinstance(output, dict):
                    audio_url = output.get("audio_out") or output.get("audio") or output.get("output")
                elif isinstance(output, list) and len(output) > 0:
                    audio_url = output[0]
                else:
                    return {"error": f"Unexpected output format: {output}"}
                
                # Download the audio file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Determine extension from URL
                if ".wav" in audio_url:
                    ext = "wav"
                elif ".mp3" in audio_url:
                    ext = "mp3"
                else:
                    ext = "wav"
                
                filename = f"replicate_tts_{timestamp}.{ext}"
                urlretrieve(audio_url, filename)
                
                return {
                    "success": True,
                    "file": filename,
                    "url": audio_url,
                    "model": model,
                    "prediction_id": status["id"],
                    "characters": len(text)
                }
            
            elif status["status"] == "failed":
                return {"error": f"Generation failed: {status.get('error', 'Unknown error')}"}
            
            elif status["status"] == "canceled":
                return {"error": "Generation was canceled"}
            
            # Still processing
            time.sleep(2)
        
        return {"error": "Generation timed out after 4 minutes"}
            
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        try:
            error_json = json.loads(error_body)
            error_message = error_json.get("detail", error_body)
        except:
            error_message = error_body
        return {"error": f"API error ({e.code}): {error_message}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="Generate speech using Replicate")
    parser.add_argument("--text", "-t", help="Text to convert to speech")
    parser.add_argument("--model", "-m", default="coqui-xtts",
                        choices=list(MODELS.keys()),
                        help="Model to use (default: coqui-xtts)")
    parser.add_argument("--language", "-l", default="en",
                        help="Language code (default: en)")
    parser.add_argument("--speaker", "-s",
                        help="URL to speaker audio file for voice cloning (XTTS only)")
    parser.add_argument("--file", "-f", help="Read text from file")
    
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
    
    print(f"Generating speech with Replicate ({args.model})...")
    print(f"Language: {args.language}")
    print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
    print()
    
    result = generate_speech(text, args.model, args.language, args.speaker)
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Audio generated successfully!")
        print(f"Saved to: {result['file']}")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
