#!/usr/bin/env python3
"""Extract keyframes from a video at regular intervals for analysis.

Outputs numbered PNG screenshots and optionally a timestamps.json mapping.
Used by app-demo-agent to analyze screen recordings before generating voiceover scripts.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: Could not read video duration: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return float(result.stdout.strip())


def get_video_resolution(video_path: str) -> tuple:
    """Get video width and height using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, None
    parts = result.stdout.strip().split(",")
    if len(parts) == 2:
        return int(parts[0]), int(parts[1])
    return None, None


def extract_frames(video_path: str, output_dir: str, interval: float,
                   max_frames: int, timestamps: bool) -> dict:
    """Extract frames from video at regular intervals.

    Args:
        video_path: Path to input video file.
        output_dir: Directory to save extracted frames.
        interval: Seconds between frame captures.
        max_frames: Maximum number of frames to extract.
        timestamps: Whether to output a timestamps.json file.

    Returns:
        Dict with extraction results.
    """
    video_path = os.path.expanduser(video_path)
    output_dir = os.path.expanduser(output_dir)

    if not os.path.isfile(video_path):
        return {"success": False, "error": f"Video not found: {video_path}"}

    # Check ffmpeg is available
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except FileNotFoundError:
        return {"success": False, "error": "FFmpeg not found. Install with: brew install ffmpeg"}

    # Get video info
    duration = get_video_duration(video_path)
    width, height = get_video_resolution(video_path)

    # Calculate frame timestamps
    frame_times = []
    t = 0.0
    while t < duration and len(frame_times) < max_frames:
        frame_times.append(t)
        t += interval

    # Always include a frame near the end if we haven't already
    if frame_times and (duration - frame_times[-1]) > interval * 0.5:
        if len(frame_times) < max_frames:
            frame_times.append(max(0, duration - 0.5))

    if not frame_times:
        return {"success": False, "error": "Video too short to extract frames"}

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Extract each frame
    extracted = []
    for i, t in enumerate(frame_times, 1):
        frame_name = f"frame_{i:03d}.png"
        frame_path = os.path.join(output_dir, frame_name)

        cmd = [
            "ffmpeg", "-y", "-v", "quiet",
            "-ss", str(t),
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "2",
            frame_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and os.path.isfile(frame_path):
            extracted.append({
                "frame": frame_name,
                "timestamp": round(t, 2),
                "path": frame_path
            })
        else:
            print(f"Warning: Failed to extract frame at {t:.1f}s", file=sys.stderr)

    # Write timestamps file
    if timestamps and extracted:
        ts_path = os.path.join(output_dir, "timestamps.json")
        ts_data = {
            "video": os.path.basename(video_path),
            "duration": round(duration, 2),
            "resolution": {"width": width, "height": height},
            "frames": extracted
        }
        with open(ts_path, "w") as f:
            json.dump(ts_data, f, indent=2)

    return {
        "success": True,
        "frames_extracted": len(extracted),
        "video_duration": round(duration, 2),
        "resolution": f"{width}x{height}" if width else "unknown",
        "output_dir": output_dir,
        "frames": [e["frame"] for e in extracted]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract keyframes from a video for analysis"
    )
    parser.add_argument("input", help="Input video file")
    parser.add_argument("-o", "--output", default="./frames/",
                        help="Output directory for frames (default: ./frames/)")
    parser.add_argument("--interval", type=float, default=2.0,
                        help="Seconds between frame captures (default: 2)")
    parser.add_argument("--max-frames", type=int, default=20,
                        help="Maximum number of frames to extract (default: 20)")
    parser.add_argument("--timestamps", action="store_true",
                        help="Output a timestamps.json mapping file")

    args = parser.parse_args()
    result = extract_frames(args.input, args.output, args.interval,
                            args.max_frames, args.timestamps)

    print(json.dumps(result, indent=2))

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
