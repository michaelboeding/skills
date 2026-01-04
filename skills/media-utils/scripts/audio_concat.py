#!/usr/bin/env python3
"""
Concatenate multiple audio files into one.
Uses FFmpeg for reliable audio stitching.
"""

import argparse
import subprocess
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime


def concat_audio(
    input_files: list,
    output_file: str = None,
    crossfade_duration: float = 0,
    normalize: bool = False
) -> dict:
    """Concatenate multiple audio files.
    
    Args:
        input_files: List of paths to audio files
        output_file: Output file path (auto-generated if None)
        crossfade_duration: Crossfade between clips in seconds (0 = no crossfade)
        normalize: Whether to normalize audio levels
    
    Returns:
        dict with success/error and output file path
    """
    if not input_files:
        return {"error": "No input files provided"}
    
    if len(input_files) == 1:
        # Just copy the single file
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"audio_concat_{timestamp}.mp3"
        
        try:
            import shutil
            shutil.copy(input_files[0], output_file)
            return {"success": True, "file": output_file, "files_concatenated": 1}
        except Exception as e:
            return {"error": f"Failed to copy file: {e}"}
    
    # Validate input files exist
    for f in input_files:
        if not os.path.exists(f):
            return {"error": f"Input file not found: {f}"}
    
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Use extension from first input file
        ext = Path(input_files[0]).suffix or ".mp3"
        output_file = f"audio_concat_{timestamp}{ext}"
    
    try:
        if crossfade_duration > 0:
            # Use complex filter for crossfade
            return _concat_with_crossfade(input_files, output_file, crossfade_duration, normalize)
        else:
            # Simple concatenation
            return _concat_simple(input_files, output_file, normalize)
    
    except Exception as e:
        return {"error": f"Concatenation failed: {e}"}


def _concat_simple(input_files: list, output_file: str, normalize: bool) -> dict:
    """Simple concatenation without crossfade."""
    
    # Create a temporary file list for FFmpeg
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for audio_file in input_files:
            # FFmpeg concat demuxer requires escaped paths
            escaped_path = audio_file.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")
        list_file = f.name
    
    try:
        # Build FFmpeg command
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
        ]
        
        if normalize:
            cmd.extend(["-af", "loudnorm=I=-16:TP=-1.5:LRA=11"])
        
        cmd.extend([
            "-c:a", "libmp3lame",  # MP3 output
            "-q:a", "2",  # High quality
            output_file
        ])
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if proc.returncode != 0:
            return {"error": f"FFmpeg error: {proc.stderr[-500:]}"}
        
        return {
            "success": True,
            "file": output_file,
            "files_concatenated": len(input_files),
            "normalized": normalize
        }
    
    finally:
        # Clean up temp file
        os.unlink(list_file)


def _concat_with_crossfade(input_files: list, output_file: str, 
                           crossfade_duration: float, normalize: bool) -> dict:
    """Concatenation with crossfade between clips."""
    
    n = len(input_files)
    
    # Build complex filter for crossfades
    # Input labels: [0:a], [1:a], [2:a], etc.
    # Crossfade between each pair
    
    inputs = []
    for f in input_files:
        inputs.extend(["-i", f])
    
    # Build filter chain
    filter_parts = []
    current_label = "[0:a]"
    
    for i in range(1, n):
        next_label = f"[{i}:a]"
        out_label = f"[a{i}]" if i < n - 1 else "[out]"
        
        filter_parts.append(
            f"{current_label}{next_label}acrossfade=d={crossfade_duration}:c1=tri:c2=tri{out_label}"
        )
        current_label = out_label
    
    filter_complex = ";".join(filter_parts)
    
    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[out]",
    ]
    
    if normalize:
        # Apply normalization after crossfade
        cmd[cmd.index("-filter_complex") + 1] += ",loudnorm=I=-16:TP=-1.5:LRA=11"
    
    cmd.extend([
        "-c:a", "libmp3lame",
        "-q:a", "2",
        output_file
    ])
    
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300
    )
    
    if proc.returncode != 0:
        return {"error": f"FFmpeg crossfade error: {proc.stderr[-500:]}"}
    
    return {
        "success": True,
        "file": output_file,
        "files_concatenated": len(input_files),
        "crossfade_duration": crossfade_duration,
        "normalized": normalize
    }


def main():
    parser = argparse.ArgumentParser(
        description="Concatenate audio files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple concatenation
  python audio_concat.py -i intro.wav segment1.wav outro.wav -o podcast.mp3
  
  # With crossfade
  python audio_concat.py -i track1.wav track2.wav --crossfade 2.0
  
  # With normalization
  python audio_concat.py -i *.wav -o mixed.mp3 --normalize
        """
    )
    
    parser.add_argument("-i", "--input", nargs="+", required=True,
                        help="Input audio files to concatenate (in order)")
    parser.add_argument("-o", "--output",
                        help="Output file path (auto-generated if not provided)")
    parser.add_argument("--crossfade", type=float, default=0,
                        help="Crossfade duration in seconds (default: 0)")
    parser.add_argument("--normalize", action="store_true",
                        help="Normalize audio levels")
    
    args = parser.parse_args()
    
    print(f"🎵 Concatenating {len(args.input)} audio files...")
    
    result = concat_audio(
        args.input,
        args.output,
        args.crossfade,
        args.normalize
    )
    
    if "error" in result:
        print(f"❌ Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✅ Created: {result['file']}")
        print(f"   Files: {result['files_concatenated']}")
        if result.get("crossfade_duration"):
            print(f"   Crossfade: {result['crossfade_duration']}s")


if __name__ == "__main__":
    main()
