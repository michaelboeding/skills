#!/usr/bin/env python3
"""
Concatenate multiple video files into one.
Handles resolution/format differences with re-encoding.
"""

import argparse
import subprocess
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime


def concat_video(
    input_files: list,
    output_file: str = None,
    transition: str = None,
    transition_duration: float = 0.5,
    resolution: str = None,
    fps: int = None
) -> dict:
    """Concatenate multiple video files.
    
    Args:
        input_files: List of paths to video files
        output_file: Output file path (auto-generated if None)
        transition: Transition type ('fade', 'dissolve', None)
        transition_duration: Duration of transition in seconds
        resolution: Target resolution ('1080p', '720p', '4k', or 'WxH')
        fps: Target frame rate
    
    Returns:
        dict with success/error and output file path
    """
    if not input_files:
        return {"error": "No input files provided"}
    
    # Validate input files exist
    for f in input_files:
        if not os.path.exists(f):
            return {"error": f"Input file not found: {f}"}
    
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"video_concat_{timestamp}.mp4"
    
    # Parse resolution
    scale_filter = None
    if resolution:
        res_map = {
            "4k": "3840:2160",
            "1080p": "1920:1080",
            "720p": "1280:720",
            "480p": "854:480"
        }
        scale = res_map.get(resolution.lower(), resolution)
        scale_filter = f"scale={scale}:force_original_aspect_ratio=decrease,pad={scale}:(ow-iw)/2:(oh-ih)/2"
    
    try:
        if transition:
            return _concat_with_transition(
                input_files, output_file, transition, 
                transition_duration, scale_filter, fps
            )
        else:
            return _concat_simple(input_files, output_file, scale_filter, fps)
    
    except Exception as e:
        return {"error": f"Concatenation failed: {e}"}


def _concat_simple(input_files: list, output_file: str, 
                   scale_filter: str, fps: int) -> dict:
    """Simple concatenation, re-encoding to ensure compatibility."""
    
    # Build filter for each input
    filter_parts = []
    for i in range(len(input_files)):
        filters = []
        if scale_filter:
            filters.append(scale_filter)
        if fps:
            filters.append(f"fps={fps}")
        
        if filters:
            filter_str = ",".join(filters)
            filter_parts.append(f"[{i}:v]{filter_str}[v{i}]")
        else:
            filter_parts.append(f"[{i}:v]null[v{i}]")
        
        # Audio - just pass through
        filter_parts.append(f"[{i}:a]anull[a{i}]")
    
    # Concat all streams
    video_inputs = "".join(f"[v{i}]" for i in range(len(input_files)))
    audio_inputs = "".join(f"[a{i}]" for i in range(len(input_files)))
    
    filter_parts.append(f"{video_inputs}concat=n={len(input_files)}:v=1:a=0[outv]")
    filter_parts.append(f"{audio_inputs}concat=n={len(input_files)}:v=0:a=1[outa]")
    
    filter_complex = ";".join(filter_parts)
    
    # Build inputs
    inputs = []
    for f in input_files:
        inputs.extend(["-i", f])
    
    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        output_file
    ]
    
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600  # 10 minute timeout
    )
    
    if proc.returncode != 0:
        return {"error": f"FFmpeg error: {proc.stderr[-500:]}"}
    
    return {
        "success": True,
        "file": output_file,
        "files_concatenated": len(input_files)
    }


def _concat_with_transition(input_files: list, output_file: str,
                            transition: str, duration: float,
                            scale_filter: str, fps: int) -> dict:
    """Concatenation with transitions between clips."""
    
    n = len(input_files)
    
    # Build inputs
    inputs = []
    for f in input_files:
        inputs.extend(["-i", f])
    
    # Build complex filter with xfade
    filter_parts = []
    
    # First, normalize all inputs
    for i in range(n):
        filters = []
        if scale_filter:
            filters.append(scale_filter)
        if fps:
            filters.append(f"fps={fps}")
        filters.append("format=yuv420p")
        
        filter_str = ",".join(filters)
        filter_parts.append(f"[{i}:v]{filter_str}[v{i}]")
    
    # Apply transitions between clips
    # Get durations of each clip to calculate offset
    durations = []
    for f in input_files:
        dur = _get_duration(f)
        if dur is None:
            return {"error": f"Could not get duration of {f}"}
        durations.append(dur)
    
    # Build xfade chain
    current_label = "[v0]"
    offset = durations[0] - duration
    
    for i in range(1, n):
        next_label = f"[v{i}]"
        out_label = f"[xf{i}]" if i < n - 1 else "[outv]"
        
        # xfade transition
        filter_parts.append(
            f"{current_label}{next_label}xfade=transition={transition}:duration={duration}:offset={offset}{out_label}"
        )
        
        current_label = out_label
        offset += durations[i] - duration
    
    # Audio crossfade
    current_audio = "[0:a]"
    audio_offset = durations[0] - duration
    
    for i in range(1, n):
        next_audio = f"[{i}:a]"
        out_audio = f"[xa{i}]" if i < n - 1 else "[outa]"
        
        filter_parts.append(
            f"{current_audio}{next_audio}acrossfade=d={duration}{out_audio}"
        )
        
        current_audio = out_audio
    
    filter_complex = ";".join(filter_parts)
    
    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        output_file
    ]
    
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600
    )
    
    if proc.returncode != 0:
        return {"error": f"FFmpeg error: {proc.stderr[-500:]}"}
    
    return {
        "success": True,
        "file": output_file,
        "files_concatenated": len(input_files),
        "transition": transition,
        "transition_duration": duration
    }


def _get_duration(file_path: str) -> float:
    """Get duration of video file in seconds."""
    try:
        proc = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        if proc.returncode == 0:
            return float(proc.stdout.strip())
    except:
        pass
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Concatenate video files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple concatenation
  python video_concat.py -i clip1.mp4 clip2.mp4 clip3.mp4 -o final.mp4
  
  # With fade transition
  python video_concat.py -i *.mp4 -o final.mp4 --transition fade --duration 1.0
  
  # Normalize to 1080p
  python video_concat.py -i *.mp4 -o final.mp4 --resolution 1080p
  
Transition types: fade, dissolve, wipeleft, wiperight, slideup, slidedown
        """
    )
    
    parser.add_argument("-i", "--input", nargs="+", required=True,
                        help="Input video files to concatenate (in order)")
    parser.add_argument("-o", "--output",
                        help="Output file path")
    parser.add_argument("--transition", "-t",
                        choices=["fade", "dissolve", "wipeleft", "wiperight", 
                                "slideup", "slidedown", "circlecrop"],
                        help="Transition type between clips")
    parser.add_argument("--duration", "-d", type=float, default=0.5,
                        help="Transition duration in seconds (default: 0.5)")
    parser.add_argument("--resolution", "-r",
                        help="Target resolution (1080p, 720p, 4k, or WxH)")
    parser.add_argument("--fps", type=int,
                        help="Target frame rate")
    
    args = parser.parse_args()
    
    print(f"🎬 Concatenating {len(args.input)} video files...")
    
    result = concat_video(
        args.input,
        args.output,
        args.transition,
        args.duration,
        args.resolution,
        args.fps
    )
    
    if "error" in result:
        print(f"❌ Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✅ Created: {result['file']}")
        print(f"   Files: {result['files_concatenated']}")
        if result.get("transition"):
            print(f"   Transition: {result['transition']} ({result['transition_duration']}s)")


if __name__ == "__main__":
    main()
