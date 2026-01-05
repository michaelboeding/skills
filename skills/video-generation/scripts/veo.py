#!/usr/bin/env python3
"""
Google Veo Video Generation Script

Supports two backends:
1. Vertex AI (recommended) - 10 requests/minute, requires GCP project
2. AI Studio (fallback) - 10 requests/day, requires API key only

Auto-detects backend based on available credentials:
- GOOGLE_CLOUD_PROJECT set → Vertex AI
- GOOGLE_API_KEY set → AI Studio

Models:
- veo-3.1 (default) - Highest quality, with audio
- veo-3.1-fast - Faster processing, with audio

Features:
- Text-to-video with audio (dialogue, sound effects, ambient)
- Image-to-video (use image as first frame)
- Reference images (up to 3 images to guide content)
- Video extension (extend existing Veo videos)
- Batch/parallel generation for multi-scene workflows
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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Check for google-genai SDK (supports both AI Studio and Vertex AI)
HAS_GENAI_SDK = False

try:
    from google import genai
    from google.genai import types
    HAS_GENAI_SDK = True
except ImportError as e:
    error_msg = str(e)
    if "incompatible architecture" in error_msg or "mach-o file" in error_msg:
        print(f"""
╭─────────────────────────────────────────────────────────────────╮
│  Architecture Mismatch Error                                    │
╰─────────────────────────────────────────────────────────────────╯

The installed packages have wrong architecture. Fix with:

   pip install --force-reinstall pydantic pydantic-core google-genai

Error: {error_msg[:100]}
""", file=sys.stderr)
    else:
        print("""
╭─────────────────────────────────────────────────────────────────╮
│  Missing Dependency: google-genai                               │
╰─────────────────────────────────────────────────────────────────╯

Install with:

   pip install google-genai

Note: Requires Python 3.10+
""", file=sys.stderr)
    sys.exit(1)


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

# Available Veo models (google-genai SDK works for both Vertex AI and AI Studio)
MODELS = {
    "veo-3.1": "veo-3.1-generate-preview",
    "veo-3.1-fast": "veo-3.1-fast-generate-preview",
}

DEFAULT_MODEL = "veo-3.1"


def get_backend() -> str:
    """Detect which backend to use based on available credentials.
    
    The google-genai SDK supports both backends:
    - Vertex AI: vertexai=True, project=..., location=...
    - AI Studio: api_key=...
    
    Returns:
        'vertex' if GCP project configured (10 req/min)
        'ai_studio' if API key configured (10 req/day)
        None if no credentials found
    """
    # Check for Vertex AI credentials (preferred - higher rate limits)
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCLOUD_PROJECT")
    
    if project_id:
        return "vertex"
    
    # Try to auto-detect project from gcloud config
    try:
        import subprocess
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            os.environ["GOOGLE_CLOUD_PROJECT"] = result.stdout.strip()
            return "vertex"
    except Exception:
        pass
    
    # Fall back to AI Studio if we have an API key
    if os.environ.get("GOOGLE_API_KEY"):
        return "ai_studio"
    
    return None


def get_genai_client():
    """Get a google-genai client configured for the detected backend."""
    backend = get_backend()
    
    if backend == "vertex":
        project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        return genai.Client(vertexai=True, project=project, location=location), backend
    elif backend == "ai_studio":
        api_key = os.environ.get("GOOGLE_API_KEY")
        return genai.Client(api_key=api_key), backend
    else:
        return None, None


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


def load_video_as_base64(video_path: str) -> tuple:
    """Load a video file and return base64 data and mime type."""
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    suffix = path.suffix.lower()
    mime_types = {
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".avi": "video/x-msvideo",
        ".webm": "video/webm",
    }
    mime_type = mime_types.get(suffix, "video/mp4")
    
    with open(path, "rb") as f:
        video_data = base64.b64encode(f.read()).decode()
    
    return video_data, mime_type


def extend_video(
    video_path: str,
    prompt: str = None,
    model: str = DEFAULT_MODEL,
    num_extensions: int = 1
) -> dict:
    """Extend an existing Veo-generated video.
    
    Args:
        video_path: Path to the video to extend (must be Veo-generated)
        prompt: Optional prompt to guide the extension
        model: Model to use (must be veo-3.1)
        num_extensions: Number of times to extend (each adds ~7 seconds)
    
    Returns:
        dict with success/error and output file path
    
    Note: 
        - Only works with Veo 3.1
        - Input video must be Veo-generated, max 141 seconds
        - Each extension adds ~7 seconds
        - Max 20 extensions total
        - Output resolution is 720p
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY environment variable not set. Get your key at https://aistudio.google.com/apikey"}
    
    if not os.path.exists(video_path):
        return {"error": f"Video file not found: {video_path}"}
    
    # Extension only works with Veo 3.1
    model_id = "veo-3.1-generate-preview"
    
    if num_extensions < 1 or num_extensions > 20:
        return {"error": "num_extensions must be between 1 and 20"}
    
    current_video_path = video_path
    final_result = None
    
    for ext_num in range(num_extensions):
        print(f"\n📹 Extension {ext_num + 1}/{num_extensions}...")
        
        try:
            # Load current video
            video_data, mime_type = load_video_as_base64(current_video_path)
        except FileNotFoundError as e:
            return {"error": str(e)}
        
        # API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateVideo?key={api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Build request data for extension
        data = {
            "video": {
                "bytesBase64Encoded": video_data,
                "mimeType": mime_type
            },
            "generationConfig": {
                "numberOfVideos": 1,
                "resolution": "720p"  # Extension only supports 720p
            }
        }
        
        if prompt:
            data["prompt"] = prompt
        
        try:
            # Create extension request
            request = Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
            with urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode())
            
            # Check for operation/job ID
            operation_name = result.get("name") or result.get("operationId")
            
            if operation_name:
                # Poll for completion
                poll_url = f"https://generativelanguage.googleapis.com/v1beta/{operation_name}?key={api_key}"
                print("Extending video... This may take a few minutes.")
                
                max_attempts = 72  # Up to 6 minutes
                for attempt in range(max_attempts):
                    try:
                        poll_request = Request(poll_url, headers=headers)
                        with urlopen(poll_request, timeout=30) as response:
                            status = json.loads(response.read().decode())
                        
                        if status.get("done"):
                            if "error" in status:
                                return {"error": f"Extension failed: {status['error']}"}
                            
                            # Extract video from response
                            video_response = status.get("response", {})
                            videos = video_response.get("generatedVideos", [])
                            
                            if not videos:
                                return {"error": "No video in extension response"}
                            
                            video_obj = videos[0].get("video", {})
                            video_uri = video_obj.get("uri") or videos[0].get("uri")
                            
                            # Download the extended video
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"veo_extended_{ext_num + 1}_{timestamp}.mp4"
                            
                            if video_uri:
                                print(f"Downloading extended video to {filename}...")
                                urlretrieve(video_uri, filename)
                            elif "bytesBase64Encoded" in video_obj:
                                print(f"Saving extended video to {filename}...")
                                video_bytes = base64.b64decode(video_obj["bytesBase64Encoded"])
                                with open(filename, "wb") as f:
                                    f.write(video_bytes)
                            else:
                                return {"error": "No video data in response"}
                            
                            # Update for next iteration
                            current_video_path = filename
                            final_result = {
                                "success": True,
                                "file": filename,
                                "model": model_id,
                                "extensions_applied": ext_num + 1,
                                "original_video": video_path,
                                "prompt": prompt
                            }
                            break
                        
                        if attempt % 6 == 0:
                            elapsed = attempt * 5
                            print(f"Still extending... ({elapsed}s elapsed)")
                        time.sleep(5)
                        
                    except Exception as poll_error:
                        if attempt < max_attempts - 1:
                            time.sleep(5)
                            continue
                        return {"error": f"Polling failed: {str(poll_error)}"}
                else:
                    return {"error": "Extension timed out after 6 minutes"}
            else:
                return {"error": f"Unexpected response: {json.dumps(result)[:200]}"}
                
        except HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            try:
                error_json = json.loads(error_body)
                error_message = error_json.get("error", {}).get("message", error_body)
            except:
                error_message = error_body
            return {"error": f"API error ({e.code}): {error_message}"}
        except Exception as e:
            return {"error": f"Extension request failed: {str(e)}"}
    
    return final_result


def generate_video_impl(prompt: str, model: str = DEFAULT_MODEL, duration: int = 8,
                        aspect_ratio: str = "16:9", resolution: str = "720p",
                        image: str = None, negative_prompt: str = None) -> dict:
    """Generate a video using Google Veo (auto-detects Vertex AI or AI Studio).
    
    Args:
        prompt: Text description for the video (supports audio cues for Veo 3+)
        model: Model to use (veo-3.1 or veo-3.1-fast)
        duration: Video duration in seconds (4, 6, or 8)
        aspect_ratio: 16:9 or 9:16
        resolution: 720p or 1080p (1080p only for 8s with Veo 3.1)
        image: Optional image path to use as first frame
        negative_prompt: What not to include in the video
    """
    # Get the appropriate client
    client, backend = get_genai_client()
    
    if client is None:
        return {"error": """No credentials found. Set one of:
  
  Vertex AI (recommended - 10 requests/minute):
    export GOOGLE_CLOUD_PROJECT=your-project-id
    gcloud auth application-default login
    
  AI Studio (simple - 10 requests/day):
    export GOOGLE_API_KEY=your-api-key
"""}
    
    # Show which backend we're using
    if backend == "vertex":
        project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        print(f"🚀 Using Vertex AI backend (10 requests/minute)")
        print(f"   Project: {project}, Location: {location}")
    else:
        print("⚠️  Using AI Studio backend (10 requests/DAY - consider setting up Vertex AI)")
    
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
    
    try:
        # client is already configured via get_genai_client()
        
        # Build generation config
        config = types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            duration_seconds=duration,
            number_of_videos=1,
        )
        
        # Add negative prompt if provided
        if negative_prompt:
            config.negative_prompt = negative_prompt
        
        # Handle image input for image-to-video
        image_obj = None
        if image:
            try:
                img_data, mime_type = load_image_as_base64(image)
                image_obj = types.Image(
                    image_bytes=base64.b64decode(img_data),
                    mime_type=mime_type
                )
            except FileNotFoundError as e:
                return {"error": str(e)}
        
        print("Generating video... This may take a few minutes.")
        print("(Veo generates high-quality video with audio - please be patient)")
        
        # Start video generation
        if image_obj:
            operation = client.models.generate_videos(
                model=model_id,
                prompt=prompt,
                image=image_obj,
                config=config
            )
        else:
            operation = client.models.generate_videos(
                model=model_id,
                prompt=prompt,
                config=config
            )
        
        # Poll for completion
        max_attempts = 72  # Up to 6 minutes
        for attempt in range(max_attempts):
            # Refresh operation status
            operation = client.operations.get(operation=operation)
            
            if operation.done:
                if operation.error:
                    return {"error": f"Generation failed: {operation.error}"}
                
                # Get the result - try different response formats
                videos = None
                if operation.response and hasattr(operation.response, 'generated_videos'):
                    videos = operation.response.generated_videos
                elif operation.result and hasattr(operation.result, 'generated_videos'):
                    videos = operation.result.generated_videos
                
                if not videos:
                    return {"error": "No videos generated"}
                
                video = videos[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"veo_{model}_{timestamp}.mp4"
                
                # Try to get video data
                video_saved = False
                if hasattr(video, 'video'):
                    if hasattr(video.video, 'video_bytes') and video.video.video_bytes:
                        # Prefer direct bytes if available
                        print(f"Saving video to {filename}...")
                        with open(filename, "wb") as f:
                            f.write(video.video.video_bytes)
                        video_saved = True
                    elif hasattr(video.video, 'uri') and video.video.uri:
                        # Download from URI with API key auth (if using AI Studio)
                        print(f"Downloading video to {filename}...")
                        video_url = video.video.uri
                        # Add API key if not already in URL and using AI Studio
                        api_key = os.environ.get("GOOGLE_API_KEY")
                        if api_key and "key=" not in video_url:
                            separator = "&" if "?" in video_url else "?"
                            video_url = f"{video_url}{separator}key={api_key}"
                        try:
                            req = Request(video_url)
                            with urlopen(req, timeout=120) as resp:
                                with open(filename, "wb") as f:
                                    f.write(resp.read())
                            video_saved = True
                        except Exception as dl_error:
                            # Try without auth as fallback
                            try:
                                urlretrieve(video.video.uri, filename)
                                video_saved = True
                            except Exception:
                                return {"error": f"Failed to download video: {dl_error}"}
                
                if not video_saved:
                    return {"error": "No video data in response"}
                
                return {
                    "success": True,
                    "file": filename,
                    "model": model_id,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "resolution": resolution,
                    "has_audio": True,  # All supported models have audio
                    "backend": backend,
                    "prompt": prompt
                }
            
            if attempt % 6 == 0:
                elapsed = attempt * 5
                print(f"Still generating... ({elapsed}s elapsed)")
            time.sleep(5)
        
        return {"error": "Generation timed out after 6 minutes"}
        
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def generate_video(prompt: str, model: str = DEFAULT_MODEL, duration: int = 8,
                   aspect_ratio: str = "16:9", resolution: str = "720p",
                   image: str = None, negative_prompt: str = None) -> dict:
    """Generate a video using the best available backend.
    
    Auto-selects backend:
    - Vertex AI if GOOGLE_CLOUD_PROJECT is set (10 RPM)
    - AI Studio if GOOGLE_API_KEY is set (10 RPD)
    
    Args:
        prompt: Text description for the video
        model: veo-3.1 (best) or veo-3.1-fast (faster)
        duration: 4, 6, or 8 seconds
        aspect_ratio: 16:9 or 9:16
        resolution: 720p or 1080p
        image: Optional image path for image-to-video
        negative_prompt: What not to include
    
    Returns:
        dict with success/error and file path
    """
    return generate_video_impl(prompt, model, duration, aspect_ratio, 
                               resolution, image, negative_prompt)


# Thread-safe state for batch mode
_print_lock = threading.Lock()
_batch_status = {}  # {idx: "pending" | "running" | "complete" | "failed"}
_batch_prompts = {}  # {idx: prompt_preview}
_batch_files = {}  # {idx: output_filename}


def _safe_print(msg: str):
    """Thread-safe print for parallel generation."""
    with _print_lock:
        print(msg)


def _update_status_display(start_time: float):
    """Print current status of all batch jobs."""
    with _print_lock:
        total = len(_batch_status)
        elapsed = time.time() - start_time
        
        # Count states
        pending = sum(1 for s in _batch_status.values() if s == "pending")
        running = sum(1 for s in _batch_status.values() if s == "running")
        complete = sum(1 for s in _batch_status.values() if s == "complete")
        failed = sum(1 for s in _batch_status.values() if s == "failed")
        
        # Build status display
        print("\n" + "─" * 60)
        print(f"📊 BATCH STATUS ({int(elapsed)}s elapsed)")
        print("─" * 60)
        
        for idx in sorted(_batch_status.keys()):
            status = _batch_status[idx]
            prompt = _batch_prompts.get(idx, "")[:40]
            scene = idx + 1
            
            if status == "pending":
                icon = "⏳"
                detail = "Waiting..."
            elif status == "running":
                icon = "🔄"
                detail = "Generating..."
            elif status == "complete":
                icon = "✅"
                detail = _batch_files.get(idx, "Done")
            else:  # failed
                icon = "❌"
                detail = "Failed"
            
            print(f"  {icon} Scene {scene}: {prompt}... → {detail}")
        
        print("─" * 60)
        print(f"  ⏳ Pending: {pending}  🔄 Running: {running}  ✅ Complete: {complete}  ❌ Failed: {failed}")
        print("─" * 60 + "\n")


def _generate_single_for_batch(idx: int, config: dict, start_time: float) -> dict:
    """Generate a single video as part of a batch (thread worker).
    
    Args:
        idx: Index of this video in the batch (0-based)
        config: Video configuration dict with prompt, model, duration, etc.
        start_time: Batch start time for elapsed tracking
    
    Returns:
        dict with index, success/error, and file path
    """
    scene_num = idx + 1
    prompt = config.get("prompt", "")
    model = config.get("model", DEFAULT_MODEL)
    duration = config.get("duration", 8)
    aspect_ratio = config.get("aspect_ratio", "16:9")
    resolution = config.get("resolution", "720p")
    image = config.get("image")
    negative_prompt = config.get("negative_prompt")
    output_name = config.get("output")  # Optional custom output filename
    
    # Update status to running
    with _print_lock:
        _batch_status[idx] = "running"
    
    _update_status_display(start_time)
    
    # Suppress individual video prints during batch by redirecting stdout temporarily
    result = generate_video(
        prompt=prompt,
        model=model,
        duration=duration,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        image=image,
        negative_prompt=negative_prompt
    )
    
    # Rename output file if custom name specified
    if result.get("success") and output_name and result.get("file"):
        try:
            os.rename(result["file"], output_name)
            result["file"] = output_name
        except OSError:
            pass  # Keep original name if rename fails
    
    # Update status
    with _print_lock:
        if result.get("success"):
            _batch_status[idx] = "complete"
            _batch_files[idx] = result.get("file", "Done")
        else:
            _batch_status[idx] = "failed"
    
    _update_status_display(start_time)
    
    result["index"] = idx
    result["scene"] = scene_num
    return result


def generate_videos_batch(configs: list, max_workers: int = 5) -> dict:
    """Generate multiple videos in parallel.
    
    Args:
        configs: List of video configuration dicts, each with:
            - prompt (required): Video description
            - model: Model to use (default: veo-3.1)
            - duration: 4, 6, or 8 seconds (default: 8)
            - aspect_ratio: "16:9" or "9:16" (default: "16:9")
            - resolution: "720p" or "1080p" (default: "720p")
            - image: Optional image path for image-to-video
            - negative_prompt: What not to include
            - output: Optional custom output filename
        max_workers: Maximum parallel generations (default: 5)
    
    Returns:
        dict with:
            - success: True if all succeeded
            - results: List of individual results
            - files: List of successfully generated files
            - failed: Count of failed generations
            - total_time: Total execution time in seconds
    """
    global _batch_status, _batch_prompts, _batch_files
    
    if not configs:
        return {"error": "No video configs provided"}
    
    # Validate all configs have prompts
    for i, cfg in enumerate(configs):
        if not cfg.get("prompt"):
            return {"error": f"Config {i+1} missing required 'prompt' field"}
    
    total = len(configs)
    
    # Initialize batch tracking
    _batch_status = {i: "pending" for i in range(total)}
    _batch_prompts = {i: cfg.get("prompt", "")[:40] for i, cfg in enumerate(configs)}
    _batch_files = {}
    
    print(f"\n🎬 Batch Video Generation")
    print(f"=" * 60)
    print(f"Videos to generate: {total}")
    print(f"Parallel workers: {min(max_workers, total)}")
    print(f"Model: {configs[0].get('model', DEFAULT_MODEL)}")
    print(f"=" * 60)
    
    start_time = time.time()
    results = []
    
    # Show initial status
    _update_status_display(start_time)
    
    # Use ThreadPoolExecutor for parallel generation
    with ThreadPoolExecutor(max_workers=min(max_workers, total)) as executor:
        # Submit all jobs
        futures = {
            executor.submit(_generate_single_for_batch, i, cfg, start_time): i
            for i, cfg in enumerate(configs)
        }
        
        # Collect results as they complete
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                idx = futures[future]
                results.append({
                    "index": idx,
                    "scene": idx + 1,
                    "error": str(e)
                })
    
    # Sort results by original index
    results.sort(key=lambda x: x.get("index", 0))
    
    elapsed = time.time() - start_time
    successful = [r for r in results if r.get("success")]
    failed_list = [r for r in results if not r.get("success")]
    
    # Final status display
    print("\n" + "═" * 60)
    print(f"🎬 BATCH COMPLETE")
    print("═" * 60)
    print(f"  Total time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    print(f"  Successful: {len(successful)}/{total}")
    if failed_list:
        print(f"  Failed: {len(failed_list)}/{total}")
    print()
    
    if successful:
        print("📁 Generated files:")
        for r in successful:
            scene = r.get("scene", r.get("index", 0) + 1)
            print(f"   Scene {scene}: {r.get('file')}")
    
    if failed_list:
        print("\n❌ Failed generations:")
        for r in failed_list:
            scene = r.get("scene", r.get("index", 0) + 1)
            error = r.get("error", "Unknown error")[:50]
            print(f"   Scene {scene}: {error}")
    
    print("═" * 60)
    
    return {
        "success": len(failed_list) == 0,
        "results": results,
        "files": [r.get("file") for r in successful if r.get("file")],
        "successful": len(successful),
        "failed": len(failed_list),
        "total": total,
        "total_time": round(elapsed, 1),
        "avg_time_per_video": round(elapsed / total, 1) if total > 0 else 0
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos using Google Veo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Models:
  veo-3.1       Highest quality, with audio (default)
  veo-3.1-fast  Faster processing, with audio

Examples:
  # Basic text-to-video
  python veo.py -p "A dog running on a beach at sunset"
  
  # With dialogue (Veo 3+)
  python veo.py -p 'A man says "Hello world!" while waving at the camera'
  
  # Image-to-video (animate an image)
  python veo.py -p "The cat slowly opens its eyes" --image cat.jpg
  
  # Faster generation
  python veo.py -p "Ocean waves" --model veo-3.1-fast
  
  # EXTEND an existing video (for continuity)
  python veo.py --extend previous.mp4 -p "Continue walking into the forest"
  
  # Extend multiple times (each adds ~7 seconds)
  python veo.py --extend clip.mp4 -p "Keep exploring" --extend-times 3

Video Extension (for long-form continuity):
  The --extend flag continues from where a previous Veo video ended.
  This creates TRUE visual continuity, not just stitching.
  - Only works with Veo-generated videos (max 141s input)
  - Each extension adds ~7 seconds
  - Output is 720p
  - Maximum 20 extensions (~2.5 minutes total)

BATCH MODE (parallel generation):
  Generate multiple videos simultaneously for faster workflows.
  
  # Create a scenes.json file:
  [
    {"prompt": "Scene 1: Hero shot of product", "duration": 6},
    {"prompt": "Scene 2: Feature highlights", "duration": 8},
    {"prompt": "Scene 3: Lifestyle usage", "duration": 8},
    {"prompt": "Scene 4: Logo and CTA", "duration": 4, "output": "scene4_cta.mp4"}
  ]
  
  # Generate all scenes in parallel:
  python veo.py --batch scenes.json
  
  # With custom worker count:
  python veo.py --batch scenes.json --max-workers 3
  
  Batch config options per video:
    - prompt (required): Video description
    - model: veo-3.1, veo-3.1-fast, etc.
    - duration: 4, 6, or 8
    - aspect_ratio: "16:9" or "9:16"
    - resolution: "720p" or "1080p"
    - image: Path to image for image-to-video
    - negative_prompt: What to avoid
    - output: Custom output filename
        """
    )
    parser.add_argument("--prompt", "-p",
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
    
    # Extension options
    parser.add_argument("--extend", "-e",
                        help="Extend an existing Veo-generated video (path to .mp4)")
    parser.add_argument("--extend-times", "-x", type=int, default=1,
                        help="Number of times to extend (each adds ~7s, max 20)")
    
    # Batch/parallel options
    parser.add_argument("--batch", "-b",
                        help="Generate multiple videos in parallel from JSON file")
    parser.add_argument("--max-workers", "-w", type=int, default=5,
                        help="Max parallel workers for batch mode (default: 5)")
    
    args = parser.parse_args()
    
    # Handle batch mode
    if args.batch:
        batch_file = Path(args.batch)
        if not batch_file.exists():
            print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
            sys.exit(1)
        
        try:
            with open(batch_file) as f:
                configs = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in batch file: {e}", file=sys.stderr)
            sys.exit(1)
        
        if not isinstance(configs, list):
            print("Error: Batch file must contain a JSON array of video configs", file=sys.stderr)
            sys.exit(1)
        
        result = generate_videos_batch(configs, args.max_workers)
        
        if result.get("error"):
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        
        print()
        print("Generated files:")
        for f in result.get("files", []):
            print(f"  - {f}")
        print()
        print(json.dumps(result, indent=2))
        
        sys.exit(0 if result.get("success") else 1)
    
    # Handle extension mode
    if args.extend:
        print(f"🎬 Extending video with Google Veo 3.1...")
        print(f"Input: {args.extend}")
        print(f"Extensions: {args.extend_times} (each adds ~7 seconds)")
        if args.prompt:
            print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
        print()
        
        result = extend_video(
            args.extend,
            args.prompt,
            "veo-3.1",  # Extension only works with Veo 3.1
            args.extend_times
        )
        
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        else:
            print()
            print("✅ Video extended successfully!")
            print(f"Saved to: {result['file']}")
            print(f"Extensions applied: {result['extensions_applied']}")
            print("Note: Extended video includes original + new content")
            print(json.dumps(result, indent=2))
        return
    
    # Regular generation mode - prompt is required
    if not args.prompt:
        parser.error("--prompt/-p is required for video generation (use --extend for extension)")
    
    if args.list_models:
        print("Available Veo models:")
        print("-" * 60)
        for name, model_id in MODELS.items():
            default = " (default)" if name == DEFAULT_MODEL else ""
            speed = "fastest" if "fast" in name else "best quality"
            print(f"  {name:15} {model_id:35} [{speed}]{default}")
        print("\nAll models include audio (dialogue, sound effects, ambient)")
        return
    
    model_id = MODELS.get(args.model, MODELS[DEFAULT_MODEL])
    
    print(f"🎬 Generating video with Google Veo...")
    print(f"Model: {model_id} (with audio)")
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
        print("✅ Video generated successfully!")
        print(f"Saved to: {result['file']}")
        if result.get("has_audio"):
            print("Audio: Included (dialogue, sound effects, ambient)")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
