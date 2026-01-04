#!/usr/bin/env python3
"""
Check if FFmpeg is installed and available.
Required for all media assembly operations.
"""

import subprocess
import sys
import shutil


def check_ffmpeg() -> dict:
    """Check if FFmpeg and FFprobe are available.
    
    Returns:
        dict with 'available' bool and version info or error
    """
    result = {
        "ffmpeg": False,
        "ffprobe": False,
        "ffmpeg_version": None,
        "ffprobe_version": None,
        "available": False,
        "error": None
    }
    
    # Check FFmpeg
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        try:
            proc = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if proc.returncode == 0:
                result["ffmpeg"] = True
                # Extract version from first line
                version_line = proc.stdout.split('\n')[0]
                result["ffmpeg_version"] = version_line
        except Exception as e:
            result["error"] = f"FFmpeg check failed: {e}"
    
    # Check FFprobe
    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path:
        try:
            proc = subprocess.run(
                ["ffprobe", "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if proc.returncode == 0:
                result["ffprobe"] = True
                version_line = proc.stdout.split('\n')[0]
                result["ffprobe_version"] = version_line
        except Exception as e:
            pass
    
    result["available"] = result["ffmpeg"] and result["ffprobe"]
    
    if not result["available"]:
        result["error"] = "FFmpeg not found. Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)"
    
    return result


def get_media_info(file_path: str) -> dict:
    """Get duration and format info for a media file.
    
    Args:
        file_path: Path to audio or video file
    
    Returns:
        dict with duration, format, streams info
    """
    try:
        proc = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if proc.returncode == 0:
            import json
            info = json.loads(proc.stdout)
            
            # Extract key info
            format_info = info.get("format", {})
            streams = info.get("streams", [])
            
            result = {
                "duration": float(format_info.get("duration", 0)),
                "format": format_info.get("format_name", "unknown"),
                "size_bytes": int(format_info.get("size", 0)),
                "bit_rate": int(format_info.get("bit_rate", 0)),
                "streams": []
            }
            
            for stream in streams:
                stream_info = {
                    "type": stream.get("codec_type"),
                    "codec": stream.get("codec_name"),
                }
                if stream.get("codec_type") == "video":
                    stream_info["width"] = stream.get("width")
                    stream_info["height"] = stream.get("height")
                    stream_info["fps"] = stream.get("r_frame_rate")
                elif stream.get("codec_type") == "audio":
                    stream_info["sample_rate"] = stream.get("sample_rate")
                    stream_info["channels"] = stream.get("channels")
                
                result["streams"].append(stream_info)
            
            return result
        else:
            return {"error": f"FFprobe failed: {proc.stderr}"}
            
    except Exception as e:
        return {"error": f"Failed to get media info: {e}"}


def main():
    """Check FFmpeg availability and print status."""
    result = check_ffmpeg()
    
    if result["available"]:
        print("✅ FFmpeg is available!")
        print(f"   {result['ffmpeg_version']}")
        print(f"   {result['ffprobe_version']}")
    else:
        print("❌ FFmpeg not available")
        print(f"   Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
