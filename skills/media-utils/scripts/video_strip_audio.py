#!/usr/bin/env python3
"""
Strip audio from video files.
Useful for replacing with custom voiceover/music.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


def strip_audio(
    input_file: str,
    output_file: str = None,
    copy_video: bool = True
) -> dict:
    """Remove audio track from a video file.
    
    Args:
        input_file: Path to input video file
        output_file: Output file path (auto-generated if None)
        copy_video: If True, copy video stream without re-encoding (faster)
    
    Returns:
        dict with success/error and output file path
    """
    if not os.path.exists(input_file):
        return {"error": f"Input file not found: {input_file}"}
    
    # Generate output filename if not provided
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"silent_{input_path.name}")
    
    try:
        if copy_video:
            # Fast path: just copy video, no re-encoding
            cmd = [
                "ffmpeg",
                "-y",
                "-i", input_file,
                "-an",  # Remove audio
                "-c:v", "copy",  # Copy video without re-encoding
                output_file
            ]
        else:
            # Re-encode video (slower but more compatible)
            cmd = [
                "ffmpeg",
                "-y",
                "-i", input_file,
                "-an",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                output_file
            ]
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if proc.returncode != 0:
            return {"error": f"FFmpeg error: {proc.stderr[-500:]}"}
        
        return {
            "success": True,
            "file": output_file,
            "input": input_file,
            "reencoded": not copy_video
        }
        
    except Exception as e:
        return {"error": f"Strip audio failed: {e}"}


def strip_audio_batch(
    input_files: list,
    output_dir: str = None,
    prefix: str = "silent_",
    copy_video: bool = True
) -> dict:
    """Strip audio from multiple video files.
    
    Args:
        input_files: List of input video file paths
        output_dir: Output directory (same as input if None)
        prefix: Prefix for output filenames
        copy_video: If True, copy video stream without re-encoding
    
    Returns:
        dict with results for each file
    """
    if not input_files:
        return {"error": "No input files provided"}
    
    results = []
    successful = 0
    failed = 0
    
    for input_file in input_files:
        if not os.path.exists(input_file):
            results.append({
                "input": input_file,
                "error": "File not found"
            })
            failed += 1
            continue
        
        input_path = Path(input_file)
        
        if output_dir:
            out_path = Path(output_dir) / f"{prefix}{input_path.name}"
        else:
            out_path = input_path.parent / f"{prefix}{input_path.name}"
        
        result = strip_audio(input_file, str(out_path), copy_video)
        results.append(result)
        
        if result.get("success"):
            successful += 1
        else:
            failed += 1
    
    return {
        "success": failed == 0,
        "results": results,
        "successful": successful,
        "failed": failed,
        "files": [r.get("file") for r in results if r.get("success")]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Strip audio from video files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Strip audio from single file
  python video_strip_audio.py -i video.mp4 -o silent_video.mp4
  
  # Strip audio from multiple files
  python video_strip_audio.py -i clip1.mp4 clip2.mp4 clip3.mp4
  
  # Strip audio and re-encode video
  python video_strip_audio.py -i video.mp4 --reencode
  
  # Batch process with custom output directory
  python video_strip_audio.py -i *.mp4 --output-dir ./silent/
        """
    )
    
    parser.add_argument("-i", "--input", nargs="+", required=True,
                        help="Input video file(s)")
    parser.add_argument("-o", "--output",
                        help="Output file path (single file mode)")
    parser.add_argument("--output-dir",
                        help="Output directory (batch mode)")
    parser.add_argument("--prefix", default="silent_",
                        help="Prefix for output filenames (default: 'silent_')")
    parser.add_argument("--reencode", action="store_true",
                        help="Re-encode video instead of copying")
    
    args = parser.parse_args()
    
    if len(args.input) == 1 and args.output:
        # Single file mode
        print(f"🔇 Stripping audio from {args.input[0]}...")
        result = strip_audio(args.input[0], args.output, not args.reencode)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"✅ Created: {result['file']}")
    else:
        # Batch mode
        print(f"🔇 Stripping audio from {len(args.input)} files...")
        result = strip_audio_batch(
            args.input, 
            args.output_dir, 
            args.prefix,
            not args.reencode
        )
        
        if result.get("failed", 0) > 0:
            print(f"⚠️  {result['successful']} succeeded, {result['failed']} failed")
            for r in result["results"]:
                if "error" in r:
                    print(f"   ❌ {r.get('input', 'unknown')}: {r['error']}")
            sys.exit(1)
        else:
            print(f"✅ Processed {result['successful']} files:")
            for f in result["files"]:
                print(f"   {f}")


if __name__ == "__main__":
    main()
