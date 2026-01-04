#!/usr/bin/env python3
"""
Mix multiple audio tracks together.
Supports ducking (lowering music volume when voice is present).
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


def mix_audio(
    voice_file: str,
    music_file: str,
    output_file: str = None,
    music_volume: float = 0.3,
    duck_music: bool = True,
    fade_in: float = 0,
    fade_out: float = 0
) -> dict:
    """Mix voice/narration with background music.
    
    Args:
        voice_file: Path to voice/narration audio
        music_file: Path to background music
        output_file: Output file path (auto-generated if None)
        music_volume: Volume level for music (0.0-1.0, default 0.3)
        duck_music: Whether to duck music when voice is present
        fade_in: Fade in duration for music in seconds
        fade_out: Fade out duration for music in seconds
    
    Returns:
        dict with success/error and output file path
    """
    # Validate inputs
    if not os.path.exists(voice_file):
        return {"error": f"Voice file not found: {voice_file}"}
    if not os.path.exists(music_file):
        return {"error": f"Music file not found: {music_file}"}
    
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"audio_mix_{timestamp}.mp3"
    
    try:
        # Get voice duration to know how long to make the mix
        voice_duration = _get_duration(voice_file)
        if voice_duration is None:
            return {"error": "Could not determine voice file duration"}
        
        # Build the filter chain
        filters = []
        
        # Music processing: volume, optional fade, loop/trim to match voice
        music_filters = []
        
        # Adjust music volume
        music_filters.append(f"volume={music_volume}")
        
        # Fade in
        if fade_in > 0:
            music_filters.append(f"afade=t=in:st=0:d={fade_in}")
        
        # Fade out at the end
        if fade_out > 0:
            fade_start = max(0, voice_duration - fade_out)
            music_filters.append(f"afade=t=out:st={fade_start}:d={fade_out}")
        
        music_filter_str = ",".join(music_filters) if music_filters else "anull"
        
        if duck_music:
            # Use sidechaincompress for ducking
            # Voice controls when music ducks
            filter_complex = (
                f"[1:a]{music_filter_str},aloop=loop=-1:size=2e+09[music];"
                f"[music]atrim=0:{voice_duration + 1}[music_trimmed];"
                f"[music_trimmed][0:a]sidechaincompress=threshold=0.02:ratio=6:attack=50:release=400[ducked];"
                f"[0:a][ducked]amix=inputs=2:duration=first:dropout_transition=2"
            )
        else:
            # Simple mix without ducking
            filter_complex = (
                f"[1:a]{music_filter_str},aloop=loop=-1:size=2e+09[music];"
                f"[music]atrim=0:{voice_duration + 1}[music_trimmed];"
                f"[0:a][music_trimmed]amix=inputs=2:duration=first:dropout_transition=2"
            )
        
        cmd = [
            "ffmpeg",
            "-y",
            "-i", voice_file,
            "-i", music_file,
            "-filter_complex", filter_complex,
            "-c:a", "libmp3lame",
            "-q:a", "2",
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
            "voice_file": voice_file,
            "music_file": music_file,
            "music_volume": music_volume,
            "ducking": duck_music,
            "duration": voice_duration
        }
        
    except Exception as e:
        return {"error": f"Mix failed: {e}"}


def mix_multiple(
    tracks: list,
    output_file: str = None,
    volumes: list = None,
    normalize: bool = True
) -> dict:
    """Mix multiple audio tracks together.
    
    Args:
        tracks: List of audio file paths
        output_file: Output file path
        volumes: List of volume levels for each track (0.0-1.0)
        normalize: Whether to normalize final output
    
    Returns:
        dict with success/error and output file path
    """
    if not tracks:
        return {"error": "No tracks provided"}
    
    # Validate all files exist
    for t in tracks:
        if not os.path.exists(t):
            return {"error": f"Track not found: {t}"}
    
    if volumes is None:
        volumes = [1.0] * len(tracks)
    
    if len(volumes) != len(tracks):
        return {"error": "Number of volumes must match number of tracks"}
    
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"audio_mix_{timestamp}.mp3"
    
    try:
        # Build inputs and filter
        inputs = []
        filter_parts = []
        
        for i, (track, vol) in enumerate(zip(tracks, volumes)):
            inputs.extend(["-i", track])
            filter_parts.append(f"[{i}:a]volume={vol}[a{i}]")
        
        # Combine all adjusted tracks
        input_labels = "".join(f"[a{i}]" for i in range(len(tracks)))
        filter_parts.append(f"{input_labels}amix=inputs={len(tracks)}:duration=longest[mixed]")
        
        if normalize:
            filter_parts.append("[mixed]loudnorm=I=-16:TP=-1.5:LRA=11")
            output_label = ""
        else:
            output_label = "-map [mixed]"
        
        filter_complex = ";".join(filter_parts)
        
        cmd = [
            "ffmpeg",
            "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-c:a", "libmp3lame",
            "-q:a", "2",
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
            "tracks_mixed": len(tracks),
            "normalized": normalize
        }
        
    except Exception as e:
        return {"error": f"Mix failed: {e}"}


def _get_duration(file_path: str) -> float:
    """Get duration of audio file in seconds."""
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
        description="Mix audio tracks (voice + music with ducking)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Mix voice with background music (music ducks under voice)
  python audio_mix.py --voice narration.wav --music background.mp3 -o final.mp3
  
  # Adjust music volume (30% is default)
  python audio_mix.py --voice voice.wav --music music.mp3 --music-volume 0.2
  
  # No ducking, just mix
  python audio_mix.py --voice voice.wav --music music.mp3 --no-duck
  
  # With fade in/out on music
  python audio_mix.py --voice voice.wav --music music.mp3 --fade-in 2 --fade-out 3
        """
    )
    
    parser.add_argument("--voice", "-v", required=True,
                        help="Voice/narration audio file")
    parser.add_argument("--music", "-m", required=True,
                        help="Background music file")
    parser.add_argument("--output", "-o",
                        help="Output file path")
    parser.add_argument("--music-volume", type=float, default=0.3,
                        help="Music volume level 0.0-1.0 (default: 0.3)")
    parser.add_argument("--no-duck", action="store_true",
                        help="Disable music ducking")
    parser.add_argument("--fade-in", type=float, default=0,
                        help="Music fade in duration in seconds")
    parser.add_argument("--fade-out", type=float, default=0,
                        help="Music fade out duration in seconds")
    
    args = parser.parse_args()
    
    print(f"🎵 Mixing voice + music...")
    print(f"   Voice: {args.voice}")
    print(f"   Music: {args.music} (volume: {args.music_volume})")
    
    result = mix_audio(
        args.voice,
        args.music,
        args.output,
        args.music_volume,
        not args.no_duck,
        args.fade_in,
        args.fade_out
    )
    
    if "error" in result:
        print(f"❌ Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✅ Created: {result['file']}")
        print(f"   Duration: {result['duration']:.1f}s")
        print(f"   Ducking: {'enabled' if result['ducking'] else 'disabled'}")


if __name__ == "__main__":
    main()
