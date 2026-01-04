#!/usr/bin/env python3
"""
Google Lyria RealTime Music Generation Script
Requires: GOOGLE_API_KEY environment variable
Requires: pip install google-genai

This wraps the Lyria RealTime WebSocket API to generate music files.
The model generates instrumental music only (no vocals).

Output: 48kHz stereo WAV file
"""

import argparse
import os
import sys
import asyncio
import struct
import wave
from datetime import datetime
from pathlib import Path

# Check for google-genai package
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("""
╭─────────────────────────────────────────────────────────────────╮
│  Missing Dependency: google-genai                               │
╰─────────────────────────────────────────────────────────────────╯

To install all skill dependencies, run:

   ./scripts/install.sh
   
Or: pip install -r requirements.txt
Or: pip install google-genai

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

# Musical scales available
SCALES = {
    "C": "C_MAJOR_A_MINOR",
    "Db": "D_FLAT_MAJOR_B_FLAT_MINOR",
    "D": "D_MAJOR_B_MINOR",
    "Eb": "E_FLAT_MAJOR_C_MINOR",
    "E": "E_MAJOR_D_FLAT_MINOR",
    "F": "F_MAJOR_D_MINOR",
    "Gb": "G_FLAT_MAJOR_E_FLAT_MINOR",
    "G": "G_MAJOR_E_MINOR",
    "Ab": "A_FLAT_MAJOR_F_MINOR",
    "A": "A_MAJOR_G_FLAT_MINOR",
    "Bb": "B_FLAT_MAJOR_G_MINOR",
    "B": "B_MAJOR_A_FLAT_MINOR",
    "auto": "SCALE_UNSPECIFIED",
}


async def generate_music(
    prompts: list,
    duration: int = 30,
    bpm: int = None,
    scale: str = "auto",
    brightness: float = None,
    density: float = None,
    temperature: float = 1.1,
    mode: str = "quality"
) -> dict:
    """Generate music using Lyria RealTime API.
    
    Args:
        prompts: List of (text, weight) tuples or just strings
        duration: Duration in seconds (default: 30)
        bpm: Beats per minute (60-200, or None for auto)
        scale: Musical scale/key (C, D, E, F, G, A, B with optional b/# or 'auto')
        brightness: Tonal brightness 0.0-1.0 (None for auto)
        density: Note density 0.0-1.0 (None for auto)
        temperature: Creativity/randomness 0.0-3.0 (default: 1.1)
        mode: 'quality' or 'diversity'
    
    Returns:
        dict with success/error and file path
    """
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY environment variable not set. Get your key at https://aistudio.google.com/apikey"}
    
    # Validate parameters
    if bpm is not None and (bpm < 60 or bpm > 200):
        return {"error": "BPM must be between 60 and 200"}
    
    if brightness is not None and (brightness < 0.0 or brightness > 1.0):
        return {"error": "Brightness must be between 0.0 and 1.0"}
    
    if density is not None and (density < 0.0 or density > 1.0):
        return {"error": "Density must be between 0.0 and 1.0"}
    
    # Get scale enum
    scale_key = scale.replace("#", "").replace("b", "b").upper()
    if scale_key.lower() == "auto":
        scale_key = "auto"
    scale_enum = SCALES.get(scale_key, SCALES.get(scale, "SCALE_UNSPECIFIED"))
    
    # Convert prompts to weighted prompts
    weighted_prompts = []
    for p in prompts:
        if isinstance(p, tuple):
            weighted_prompts.append(types.WeightedPrompt(text=p[0], weight=p[1]))
        else:
            weighted_prompts.append(types.WeightedPrompt(text=p, weight=1.0))
    
    # Collect audio chunks
    audio_chunks = []
    total_samples = 0
    target_samples = duration * 48000  # 48kHz sample rate
    
    print(f"🎵 Connecting to Lyria RealTime...")
    print(f"Duration: {duration}s | BPM: {bpm or 'auto'} | Scale: {scale}")
    print(f"Prompts: {', '.join(p.text for p in weighted_prompts)}")
    print()
    
    try:
        client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
        
        async def receive_audio(session):
            nonlocal audio_chunks, total_samples
            try:
                async for message in session.receive():
                    if hasattr(message, 'server_content') and message.server_content:
                        if hasattr(message.server_content, 'audio_chunks') and message.server_content.audio_chunks:
                            chunk = message.server_content.audio_chunks[0].data
                            audio_chunks.append(chunk)
                            # Each sample is 2 bytes (16-bit) * 2 channels
                            samples_in_chunk = len(chunk) // 4
                            total_samples += samples_in_chunk
                            
                            # Progress indicator
                            progress = min(100, int(total_samples / target_samples * 100))
                            if total_samples % (48000 * 5) < samples_in_chunk:  # Every ~5 seconds
                                elapsed = total_samples / 48000
                                print(f"  Generating... {elapsed:.0f}s / {duration}s ({progress}%)")
                    
                    # Small yield to prevent blocking
                    await asyncio.sleep(0.001)
                    
                    # Check if we have enough audio
                    if total_samples >= target_samples:
                        break
            except asyncio.CancelledError:
                pass
        
        async with client.aio.live.music.connect(model='models/lyria-realtime-exp') as session:
            # Set prompts
            await session.set_weighted_prompts(prompts=weighted_prompts)
            
            # Build config
            config_kwargs = {
                'temperature': temperature,
            }
            
            if bpm is not None:
                config_kwargs['bpm'] = bpm
            
            if brightness is not None:
                config_kwargs['brightness'] = brightness
            
            if density is not None:
                config_kwargs['density'] = density
            
            # Set scale if specified
            if scale_enum != "SCALE_UNSPECIFIED":
                config_kwargs['scale'] = getattr(types.Scale, scale_enum, types.Scale.SCALE_UNSPECIFIED)
            
            # Set mode
            if mode.lower() == 'diversity':
                config_kwargs['music_generation_mode'] = types.MusicGenerationMode.DIVERSITY
            else:
                config_kwargs['music_generation_mode'] = types.MusicGenerationMode.QUALITY
            
            await session.set_music_generation_config(
                config=types.LiveMusicGenerationConfig(**config_kwargs)
            )
            
            # Start playback and collection
            await session.play()
            
            # Create task to receive audio
            receive_task = asyncio.create_task(receive_audio(session))
            
            # Wait for duration + buffer
            try:
                await asyncio.wait_for(receive_task, timeout=duration + 10)
            except asyncio.TimeoutError:
                receive_task.cancel()
                try:
                    await receive_task
                except asyncio.CancelledError:
                    pass
            
            # Stop playback
            await session.stop()
        
        if not audio_chunks:
            return {"error": "No audio data received from Lyria"}
        
        # Combine all audio chunks
        print(f"\n  Processing {len(audio_chunks)} audio chunks...")
        all_audio = b''.join(audio_chunks)
        
        # Trim to exact duration
        target_bytes = target_samples * 4  # 2 bytes * 2 channels
        if len(all_audio) > target_bytes:
            all_audio = all_audio[:target_bytes]
        
        # Save as WAV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_slug = prompts[0] if isinstance(prompts[0], str) else prompts[0][0]
        prompt_slug = prompt_slug.replace(" ", "_")[:20]
        filename = f"lyria_{prompt_slug}_{timestamp}.wav"
        
        print(f"  Saving to {filename}...")
        
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(48000)  # 48kHz
            wav_file.writeframes(all_audio)
        
        actual_duration = len(all_audio) / 4 / 48000
        
        return {
            "success": True,
            "file": filename,
            "duration": round(actual_duration, 1),
            "sample_rate": 48000,
            "channels": 2,
            "bit_depth": 16,
            "model": "lyria-realtime-exp",
            "prompts": [p.text for p in weighted_prompts],
            "bpm": bpm or "auto",
            "scale": scale,
            "instrumental": True,  # Lyria is always instrumental
        }
        
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "401" in error_msg:
            return {"error": f"API key error: {error_msg}. Make sure GOOGLE_API_KEY is set."}
        return {"error": f"Generation failed: {error_msg}"}


def main():
    parser = argparse.ArgumentParser(
        description="Generate instrumental music using Google Lyria RealTime",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
NOTE: Lyria generates INSTRUMENTAL music only (no vocals).
      Uses the same GOOGLE_API_KEY as video/image generation.

Examples:
  # Simple generation
  python lyria.py -p "chill lofi hip hop, jazzy piano"
  
  # With BPM and duration
  python lyria.py -p "minimal techno, deep bass" --bpm 128 --duration 60
  
  # Multiple prompts with weights
  python lyria.py -p "ambient, ethereal" -p "piano, soft" --duration 45
  
  # Specific key/scale
  python lyria.py -p "jazz fusion" --scale "Bb" --bpm 95

Prompt ideas:
  Genres: lo-fi hip hop, minimal techno, ambient, jazz fusion, synthwave, 
          classical, electronic, chillout, drum & bass, indie folk
  
  Instruments: piano, guitar, synthesizer, drums, bass, strings, brass,
               808 drums, Rhodes piano, Moog synths
  
  Moods: chill, energetic, dreamy, dark, upbeat, melancholic, epic
        """
    )
    parser.add_argument("--prompt", "-p", action="append", required=True,
                        help="Music prompt (can specify multiple)")
    parser.add_argument("--duration", "-d", type=int, default=30,
                        help="Duration in seconds (default: 30)")
    parser.add_argument("--bpm", "-b", type=int,
                        help="Beats per minute (60-200, default: auto)")
    parser.add_argument("--scale", "-s", default="auto",
                        choices=list(SCALES.keys()),
                        help="Musical scale/key (default: auto)")
    parser.add_argument("--brightness", type=float,
                        help="Tonal brightness 0.0-1.0 (default: auto)")
    parser.add_argument("--density", type=float,
                        help="Note density 0.0-1.0 (default: auto)")
    parser.add_argument("--temperature", "-t", type=float, default=1.1,
                        help="Creativity 0.0-3.0 (default: 1.1)")
    parser.add_argument("--mode", "-m", choices=["quality", "diversity"], default="quality",
                        help="Generation mode (default: quality)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Google Lyria RealTime - Instrumental Music Generation")
    print("=" * 60)
    print()
    print("⚠️  Note: Lyria generates INSTRUMENTAL music only (no vocals)")
    print("    For songs with vocals, use Suno or Udio instead.")
    print()
    
    # Run async generation
    result = asyncio.run(generate_music(
        prompts=args.prompt,
        duration=args.duration,
        bpm=args.bpm,
        scale=args.scale,
        brightness=args.brightness,
        density=args.density,
        temperature=args.temperature,
        mode=args.mode
    ))
    
    if "error" in result:
        print(f"\n❌ Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print()
        print("✅ Music generated successfully!")
        print(f"   File: {result['file']}")
        print(f"   Duration: {result['duration']}s")
        print(f"   Format: {result['sample_rate']}Hz, {result['channels']}ch, {result['bit_depth']}-bit WAV")
        import json
        print()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
