#!/usr/bin/env python3
"""
Merge audio track(s) with video.
Can replace video audio or mix with existing.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime


def merge_video_audio(
    video_file: str,
    audio_file: str,
    output_file: str = None,
    replace_audio: bool = True,
    audio_volume: float = 1.0,
    video_volume: float = 0.0,
    sync_offset: float = 0
) -> dict:
    """Merge audio track with video.
    
    Args:
        video_file: Path to video file
        audio_file: Path to audio file to add
        output_file: Output file path (auto-generated if None)
        replace_audio: If True, replace video audio. If False, mix with it.
        audio_volume: Volume of the audio track (0.0-1.0)
        video_volume: Volume of original video audio (0.0-1.0, only used if not replacing)
        sync_offset: Audio offset in seconds (positive = delay audio)
    
    Returns:
        dict with success/error and output file path
    """
    # Validate inputs
    if not os.path.exists(video_file):
        return {"error": f"Video file not found: {video_file}"}
    if not os.path.exists(audio_file):
        return {"error": f"Audio file not found: {audio_file}"}
    
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"video_merged_{timestamp}.mp4"
    
    try:
        if replace_audio:
            # Simple replacement - just use the new audio
            cmd = [
                "ffmpeg",
                "-y",
                "-i", video_file,
                "-i", audio_file,
                "-c:v", "copy",  # Don't re-encode video
                "-map", "0:v:0",  # Use video from first input
                "-map", "1:a:0",  # Use audio from second input
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",  # End when shortest stream ends
            ]
            
            if sync_offset != 0:
                # Add audio delay/advance
                if sync_offset > 0:
                    cmd.extend(["-itsoffset", str(sync_offset)])
                else:
                    # Negative offset - trim beginning of audio
                    cmd.extend(["-ss", str(abs(sync_offset))])
            
            cmd.append(output_file)
            
        else:
            # Mix audio with original video audio
            filter_parts = []
            
            # Adjust volumes
            if video_volume != 1.0:
                filter_parts.append(f"[0:a]volume={video_volume}[va]")
                video_audio_label = "[va]"
            else:
                video_audio_label = "[0:a]"
            
            if audio_volume != 1.0:
                filter_parts.append(f"[1:a]volume={audio_volume}[aa]")
                new_audio_label = "[aa]"
            else:
                new_audio_label = "[1:a]"
            
            # Handle sync offset
            if sync_offset != 0:
                if sync_offset > 0:
                    filter_parts.append(f"[1:a]adelay={int(sync_offset*1000)}|{int(sync_offset*1000)}[delayed]")
                    new_audio_label = "[delayed]"
                # Negative offset would need different handling
            
            # Mix the two audio streams
            filter_parts.append(f"{video_audio_label}{new_audio_label}amix=inputs=2:duration=first[mixed]")
            
            filter_complex = ";".join(filter_parts)
            
            cmd = [
                "ffmpeg",
                "-y",
                "-i", video_file,
                "-i", audio_file,
                "-filter_complex", filter_complex,
                "-map", "0:v:0",
                "-map", "[mixed]",
                "-c:v", "copy",
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
            "video_file": video_file,
            "audio_file": audio_file,
            "replaced_audio": replace_audio,
            "sync_offset": sync_offset
        }
        
    except Exception as e:
        return {"error": f"Merge failed: {e}"}


def add_multiple_audio_tracks(
    video_file: str,
    voice_file: str = None,
    music_file: str = None,
    output_file: str = None,
    voice_volume: float = 1.0,
    music_volume: float = 0.3,
    duck_music: bool = True
) -> dict:
    """Add voice and music tracks to video (common use case).
    
    Args:
        video_file: Path to video file
        voice_file: Path to voice/narration audio
        music_file: Path to background music
        output_file: Output file path
        voice_volume: Volume for voice track
        music_volume: Volume for music track
        duck_music: Whether to duck music when voice is present
    
    Returns:
        dict with success/error and output file path
    """
    if not os.path.exists(video_file):
        return {"error": f"Video file not found: {video_file}"}
    
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"video_with_audio_{timestamp}.mp4"
    
    try:
        inputs = ["-i", video_file]
        filter_parts = []
        audio_streams = []
        
        # Add voice track
        if voice_file and os.path.exists(voice_file):
            inputs.extend(["-i", voice_file])
            voice_idx = len(inputs) // 2 - 1
            if voice_volume != 1.0:
                filter_parts.append(f"[{voice_idx}:a]volume={voice_volume}[voice]")
                audio_streams.append("[voice]")
            else:
                audio_streams.append(f"[{voice_idx}:a]")
        
        # Add music track
        if music_file and os.path.exists(music_file):
            inputs.extend(["-i", music_file])
            music_idx = len(inputs) // 2 - 1
            
            music_filters = [f"volume={music_volume}"]
            
            # Loop music if needed and trim to video length
            video_duration = _get_duration(video_file)
            if video_duration:
                music_filters.append(f"aloop=loop=-1:size=2e+09")
                music_filters.append(f"atrim=0:{video_duration}")
            
            filter_parts.append(f"[{music_idx}:a]{','.join(music_filters)}[music_adj]")
            
            if duck_music and voice_file:
                # Use sidechaincompress for ducking
                voice_label = audio_streams[-1]
                filter_parts.append(
                    f"[music_adj]{voice_label}sidechaincompress=threshold=0.02:ratio=6:attack=50:release=400[music_ducked]"
                )
                audio_streams.append("[music_ducked]")
            else:
                audio_streams.append("[music_adj]")
        
        if not audio_streams:
            return {"error": "No audio files provided"}
        
        # Mix all audio streams
        if len(audio_streams) > 1:
            stream_labels = "".join(audio_streams)
            filter_parts.append(f"{stream_labels}amix=inputs={len(audio_streams)}:duration=first[final_audio]")
            output_audio = "[final_audio]"
        else:
            output_audio = audio_streams[0]
        
        filter_complex = ";".join(filter_parts) if filter_parts else None
        
        cmd = [
            "ffmpeg",
            "-y",
            *inputs,
        ]
        
        if filter_complex:
            cmd.extend(["-filter_complex", filter_complex])
            cmd.extend(["-map", "0:v:0", "-map", output_audio])
        else:
            cmd.extend(["-map", "0:v:0", "-map", "1:a:0"])
        
        cmd.extend([
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_file
        ])
        
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
            "voice_file": voice_file,
            "music_file": music_file,
            "duck_music": duck_music
        }
        
    except Exception as e:
        return {"error": f"Failed to add audio: {e}"}


def _get_duration(file_path: str) -> float:
    """Get duration of media file in seconds."""
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
        description="Merge audio with video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Replace video audio with new audio
  python video_audio_merge.py --video clip.mp4 --audio voiceover.mp3 -o final.mp4
  
  # Mix new audio with existing video audio
  python video_audio_merge.py --video clip.mp4 --audio music.mp3 --mix
  
  # Add voice + music with ducking
  python video_audio_merge.py --video clip.mp4 --voice narration.wav --music bg.mp3
  
  # Sync offset (delay audio by 0.5 seconds)
  python video_audio_merge.py --video clip.mp4 --audio audio.mp3 --offset 0.5
        """
    )
    
    parser.add_argument("--video", "-v", required=True,
                        help="Video file")
    parser.add_argument("--audio", "-a",
                        help="Audio file to merge")
    parser.add_argument("--voice",
                        help="Voice/narration audio file")
    parser.add_argument("--music", "-m",
                        help="Background music file")
    parser.add_argument("--output", "-o",
                        help="Output file path")
    parser.add_argument("--mix", action="store_true",
                        help="Mix with existing video audio instead of replacing")
    parser.add_argument("--audio-volume", type=float, default=1.0,
                        help="Volume for audio track (0.0-1.0)")
    parser.add_argument("--music-volume", type=float, default=0.3,
                        help="Volume for music track (0.0-1.0)")
    parser.add_argument("--no-duck", action="store_true",
                        help="Disable music ducking under voice")
    parser.add_argument("--offset", type=float, default=0,
                        help="Audio sync offset in seconds")
    
    args = parser.parse_args()
    
    if args.voice or args.music:
        # Multi-track mode
        print(f"🎬 Adding audio tracks to video...")
        result = add_multiple_audio_tracks(
            args.video,
            args.voice,
            args.music,
            args.output,
            args.audio_volume,
            args.music_volume,
            not args.no_duck
        )
    elif args.audio:
        # Simple merge mode
        print(f"🎬 Merging audio with video...")
        result = merge_video_audio(
            args.video,
            args.audio,
            args.output,
            not args.mix,
            args.audio_volume,
            0.5 if args.mix else 0,
            args.offset
        )
    else:
        print("Error: Provide --audio or --voice/--music", file=sys.stderr)
        sys.exit(1)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✅ Created: {result['file']}")


if __name__ == "__main__":
    main()
