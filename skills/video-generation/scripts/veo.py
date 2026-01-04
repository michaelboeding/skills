#!/usr/bin/env python3
"""
Google Veo Video Generation Script
Requires: GOOGLE_API_KEY environment variable

Models (newest to oldest):
- veo-3.1-generate-preview (Veo 3.1 - latest, with audio, reference images, extensions)
- veo-3.1-fast-generate-preview (Veo 3.1 Fast - faster, with audio)
- veo-3-generate-preview (Veo 3 - with audio)
- veo-3-fast-generate-preview (Veo 3 Fast - faster, with audio)
- veo-2 (Veo 2 - silent, older)

Features (Veo 3.1):
- Text-to-video with audio (dialogue, sound effects, ambient)
- Image-to-video (use image as first frame)
- Reference images (up to 3 images to guide content)
- First/last frame interpolation
- Video extension (extend existing Veo videos)
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

# Available Veo models
MODELS = {
    "veo-3.1": "veo-3.1-generate-preview",
    "veo-3.1-fast": "veo-3.1-fast-generate-preview",
    "veo-3": "veo-3-generate-preview",
    "veo-3-fast": "veo-3-fast-generate-preview",
    "veo-2": "veo-2",
}

DEFAULT_MODEL = "veo-3.1"


def load_image_as_base64(image_path: str) -> tuple:
    """Load an image file and return base64 data and mime type."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    suffix = path.suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    mime_type = mime_types.get(suffix, "image/png")
    
    with open(path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    return image_data, mime_type


def generate_video(prompt: str, model: str = DEFAULT_MODEL, duration: int = 8,
                   aspect_ratio: str = "16:9", resolution: str = "720p",
                   image: str = None, negative_prompt: str = None) -> dict:
    """Generate a video using Google Veo API.
    
    Args:
        prompt: Text description for the video (supports audio cues for Veo 3+)
        model: Model to use (veo-3.1, veo-3.1-fast, veo-3, veo-3-fast, veo-2)
        duration: Video duration in seconds (4, 6, or 8)
        aspect_ratio: 16:9 or 9:16
        resolution: 720p or 1080p (1080p only for 8s with Veo 3.1)
        image: Optional image path to use as first frame
        negative_prompt: What not to include in the video
    """
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY environment variable not set. Get your key at https://aistudio.google.com/apikey"}
    
    # Get model ID
    model_id = MODELS.get(model, MODELS[DEFAULT_MODEL])
    
    # Validate parameters
    valid_durations = [4, 6, 8]
    if duration not in valid_durations:
        return {"error": f"Duration must be one of: {valid_durations}"}
    
    valid_aspect_ratios = ["16:9", "9:16"]
    if aspect_ratio not in valid_aspect_ratios:
        return {"error": f"Invalid aspect ratio. Must be one of: {valid_aspect_ratios}"}
    
    valid_resolutions = ["720p", "1080p"]
    if resolution not in valid_resolutions:
        return {"error": f"Invalid resolution. Must be one of: {valid_resolutions}"}
    
    # 1080p restrictions
    if resolution == "1080p" and duration != 8:
        return {"error": "1080p resolution only supports 8 second duration"}
    
    # API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateVideo?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Build request data
    data = {
        "prompt": prompt,
        "generationConfig": {
            "videoDuration": f"{duration}s",
            "aspectRatio": aspect_ratio,
            "resolution": resolution,
            "numberOfVideos": 1
        }
    }
    
    if negative_prompt:
        data["negativePrompt"] = negative_prompt
    
    # Add image if provided (for image-to-video)
    if image:
        try:
            img_data, mime_type = load_image_as_base64(image)
            data["image"] = {
                "bytesBase64Encoded": img_data,
                "mimeType": mime_type
            }
        except FileNotFoundError as e:
            return {"error": str(e)}
    
    try:
        # Create generation request
        request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode())
        
        # Check for operation/job ID
        operation_name = result.get("name") or result.get("operationId")
        
        if operation_name:
            # Poll for completion
            poll_url = f"https://generativelanguage.googleapis.com/v1beta/{operation_name}?key={api_key}"
            print("Generating video... This may take a few minutes.")
            print("(Veo generates high-quality video with audio - please be patient)")
            
            max_attempts = 72  # Up to 6 minutes
            for attempt in range(max_attempts):
                try:
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
                        video_obj = video_data.get("video", {})
                        video_uri = video_obj.get("uri") or video_data.get("uri")
                        
                        # Download or decode video
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"veo_{model}_{timestamp}.mp4"
                        
                        if video_uri:
                            print(f"Downloading video to {filename}...")
                            urlretrieve(video_uri, filename)
                        elif "bytesBase64Encoded" in video_obj:
                            print(f"Saving video to {filename}...")
                            video_bytes = base64.b64decode(video_obj["bytesBase64Encoded"])
                            with open(filename, "wb") as f:
                                f.write(video_bytes)
                        else:
                            return {"error": "No video data in response"}
                        
                        return {
                            "success": True,
                            "file": filename,
                            "model": model_id,
                            "duration": duration,
                            "aspect_ratio": aspect_ratio,
                            "resolution": resolution,
                            "has_audio": model in ["veo-3.1", "veo-3.1-fast", "veo-3", "veo-3-fast"],
                            "prompt": prompt
                        }
                    
                    if attempt % 6 == 0:
                        elapsed = attempt * 5
                        print(f"Still generating... ({elapsed}s elapsed)")
                    time.sleep(5)
                    
                except Exception as poll_error:
                    if attempt < max_attempts - 1:
                        time.sleep(5)
                        continue
                    return {"error": f"Polling failed: {str(poll_error)}"}
            
            return {"error": "Generation timed out after 6 minutes"}
        
        else:
            # Synchronous response (unlikely but handle it)
            videos = result.get("generatedVideos", [])
            if videos:
                video_data = videos[0]
                video_obj = video_data.get("video", {})
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"veo_{model}_{timestamp}.mp4"
                
                if "bytesBase64Encoded" in video_obj:
                    video_bytes = base64.b64decode(video_obj["bytesBase64Encoded"])
                    with open(filename, "wb") as f:
                        f.write(video_bytes)
                    
                    return {
                        "success": True,
                        "file": filename,
                        "model": model_id,
                        "duration": duration,
                        "aspect_ratio": aspect_ratio,
                        "resolution": resolution,
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
    parser = argparse.ArgumentParser(
        description="Generate videos using Google Veo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Models (newest first):
  veo-3.1       Veo 3.1 - Latest, with audio, reference images, extensions (default)
  veo-3.1-fast  Veo 3.1 Fast - Faster processing, with audio
  veo-3         Veo 3 - With audio
  veo-3-fast    Veo 3 Fast - Faster, with audio
  veo-2         Veo 2 - Silent, older

Examples:
  # Basic text-to-video
  python veo.py -p "A dog running on a beach at sunset"
  
  # With dialogue (Veo 3+)
  python veo.py -p 'A man says "Hello world!" while waving at the camera'
  
  # Image-to-video (animate an image)
  python veo.py -p "The cat slowly opens its eyes" --image cat.jpg
  
  # Faster generation
  python veo.py -p "Ocean waves" --model veo-3.1-fast
        """
    )
    parser.add_argument("--prompt", "-p", required=True, 
                        help="Video prompt (use quotes for dialogue with Veo 3+)")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL,
                        choices=list(MODELS.keys()),
                        help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--duration", "-d", type=int, default=8,
                        choices=[4, 6, 8],
                        help="Duration in seconds (default: 8)")
    parser.add_argument("--aspect-ratio", "-a", default="16:9",
                        choices=["16:9", "9:16"],
                        help="Aspect ratio (default: 16:9)")
    parser.add_argument("--resolution", "-r", default="720p",
                        choices=["720p", "1080p"],
                        help="Resolution (default: 720p, 1080p only for 8s)")
    parser.add_argument("--image", "-i",
                        help="Image to use as first frame (image-to-video)")
    parser.add_argument("--negative-prompt", "-n",
                        help="What NOT to include in the video")
    parser.add_argument("--list-models", "-l", action="store_true",
                        help="List available models")
    parser.add_argument("--silent", "-s", action="store_true",
                        help="Generate silent video (uses veo-2, no audio)")
    
    args = parser.parse_args()
    
    # --silent flag overrides model to veo-2
    if args.silent:
        args.model = "veo-2"
    
    if args.list_models:
        print("Available Veo models:")
        print("-" * 60)
        for name, model_id in MODELS.items():
            default = " (default)" if name == DEFAULT_MODEL else ""
            audio = "with audio" if name != "veo-2" else "silent"
            print(f"  {name:15} {model_id:30} [{audio}]{default}")
        return
    
    model_id = MODELS.get(args.model, MODELS[DEFAULT_MODEL])
    has_audio = args.model in ["veo-3.1", "veo-3.1-fast", "veo-3", "veo-3-fast"]
    
    print(f"🎬 Generating video with Google Veo...")
    print(f"Model: {model_id} {'(with audio)' if has_audio else '(silent)'}")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print(f"Duration: {args.duration}s, Aspect: {args.aspect_ratio}, Resolution: {args.resolution}")
    if args.image:
        print(f"First frame: {args.image}")
    print()
    
    result = generate_video(
        args.prompt, 
        args.model, 
        args.duration,
        args.aspect_ratio,
        args.resolution,
        args.image,
        args.negative_prompt
    )
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✓ Video generated successfully!")
        print(f"Saved to: {result['file']}")
        if result.get("has_audio"):
            print("Audio: Included (dialogue, sound effects, ambient)")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
