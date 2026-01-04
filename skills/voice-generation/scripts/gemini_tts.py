#!/usr/bin/env python3
"""
Google Gemini Text-to-Speech Script
Requires: GOOGLE_API_KEY environment variable
Requires: pip install google-genai

Features:
- Single-speaker and multi-speaker (up to 2) TTS
- 30 voice options with natural language style control
- Control style, accent, pace via prompts
- 24 languages with auto-detection

Output: 24kHz mono WAV file
"""

import argparse
import os
import sys
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

# Available voices with descriptions
VOICES = {
    # Bright/Upbeat
    "Zephyr": "Bright",
    "Puck": "Upbeat",
    "Aoede": "Breezy",
    "Autonoe": "Bright",
    "Laomedeia": "Upbeat",
    "Sadachbia": "Lively",
    
    # Firm/Informative
    "Charon": "Informative",
    "Kore": "Firm",
    "Orus": "Firm",
    "Rasalgethi": "Informative",
    "Alnilam": "Firm",
    
    # Soft/Gentle
    "Achernar": "Soft",
    "Vindemiatrix": "Gentle",
    "Sulafat": "Warm",
    
    # Smooth/Easy-going
    "Callirrhoe": "Easy-going",
    "Umbriel": "Easy-going",
    "Algieba": "Smooth",
    "Despina": "Smooth",
    
    # Clear/Forward
    "Erinome": "Clear",
    "Iapetus": "Clear",
    "Pulcherrima": "Forward",
    
    # Character voices
    "Fenrir": "Excitable",
    "Leda": "Youthful",
    "Enceladus": "Breathy",
    "Algenib": "Gravelly",
    "Gacrux": "Mature",
    
    # Conversational
    "Achird": "Friendly",
    "Zubenelgenubi": "Casual",
    "Schedar": "Even",
    "Sadaltager": "Knowledgeable",
}

# Models
MODELS = {
    "flash": "gemini-2.5-flash-preview-tts",
    "pro": "gemini-2.5-pro-preview-tts",
}

DEFAULT_VOICE = "Kore"
DEFAULT_MODEL = "flash"


def save_wave_file(filename: str, pcm_data: bytes, channels: int = 1, 
                   rate: int = 24000, sample_width: int = 2):
    """Save PCM audio data to a WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def generate_speech_single(
    text: str,
    voice: str = DEFAULT_VOICE,
    model: str = DEFAULT_MODEL,
    style: str = None
) -> dict:
    """Generate single-speaker speech.
    
    Args:
        text: Text to speak (can include style directions)
        voice: Voice name from VOICES
        model: 'flash' or 'pro'
        style: Optional style/direction prefix (e.g., "Say cheerfully:")
    
    Returns:
        dict with success/error and file path
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY environment variable not set. Get your key at https://aistudio.google.com/apikey"}
    
    # Validate voice
    if voice not in VOICES:
        return {"error": f"Unknown voice: {voice}. Available: {', '.join(VOICES.keys())}"}
    
    # Get model ID
    model_id = MODELS.get(model, MODELS[DEFAULT_MODEL])
    
    # Build the content with optional style prefix
    content = text
    if style:
        content = f"{style}\n\n{text}"
    
    try:
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model=model_id,
            contents=content,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice,
                        )
                    )
                ),
            )
        )
        
        # Extract audio data
        if not response.candidates or not response.candidates[0].content.parts:
            return {"error": "No audio data in response"}
        
        audio_data = response.candidates[0].content.parts[0].inline_data.data
        
        if not audio_data:
            return {"error": "Empty audio data received"}
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gemini_tts_{voice.lower()}_{timestamp}.wav"
        
        save_wave_file(filename, audio_data)
        
        return {
            "success": True,
            "file": filename,
            "voice": voice,
            "voice_style": VOICES.get(voice, ""),
            "model": model_id,
            "text_length": len(text),
            "sample_rate": 24000,
            "channels": 1,
        }
        
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "401" in error_msg:
            return {"error": f"API key error: {error_msg}"}
        return {"error": f"Generation failed: {error_msg}"}


def generate_speech_multi(
    text: str,
    speakers: list,
    model: str = DEFAULT_MODEL
) -> dict:
    """Generate multi-speaker speech (dialogue).
    
    Args:
        text: Dialogue text with speaker names
        speakers: List of (speaker_name, voice_name) tuples
        model: 'flash' or 'pro'
    
    Returns:
        dict with success/error and file path
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY environment variable not set. Get your key at https://aistudio.google.com/apikey"}
    
    if len(speakers) > 2:
        return {"error": "Gemini TTS supports maximum 2 speakers"}
    
    # Validate voices
    for speaker_name, voice in speakers:
        if voice not in VOICES:
            return {"error": f"Unknown voice '{voice}' for speaker '{speaker_name}'. Available: {', '.join(VOICES.keys())}"}
    
    # Get model ID
    model_id = MODELS.get(model, MODELS[DEFAULT_MODEL])
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Build speaker configs
        speaker_voice_configs = [
            types.SpeakerVoiceConfig(
                speaker=speaker_name,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice,
                    )
                )
            )
            for speaker_name, voice in speakers
        ]
        
        response = client.models.generate_content(
            model=model_id,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=speaker_voice_configs
                    )
                )
            )
        )
        
        # Extract audio data
        if not response.candidates or not response.candidates[0].content.parts:
            return {"error": "No audio data in response"}
        
        audio_data = response.candidates[0].content.parts[0].inline_data.data
        
        if not audio_data:
            return {"error": "Empty audio data received"}
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        speaker_names = "_".join([s[0].replace(" ", "")[:10] for s in speakers])
        filename = f"gemini_tts_multi_{speaker_names}_{timestamp}.wav"
        
        save_wave_file(filename, audio_data)
        
        return {
            "success": True,
            "file": filename,
            "speakers": [{"name": s[0], "voice": s[1]} for s in speakers],
            "model": model_id,
            "text_length": len(text),
            "sample_rate": 24000,
            "channels": 1,
        }
        
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "401" in error_msg:
            return {"error": f"API key error: {error_msg}"}
        return {"error": f"Generation failed: {error_msg}"}


def main():
    parser = argparse.ArgumentParser(
        description="Generate speech using Google Gemini TTS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
SINGLE SPEAKER EXAMPLES:

  # Basic TTS
  python gemini_tts.py -t "Hello, welcome to our podcast!"
  
  # With specific voice
  python gemini_tts.py -t "Breaking news..." --voice Charon
  
  # With style direction
  python gemini_tts.py -t "Have a wonderful day!" --style "Say cheerfully:"
  
  # With accent direction
  python gemini_tts.py -t "Hello there, mate!" \\
    --style "Speak with a British accent from London:"

MULTI-SPEAKER EXAMPLES:

  # Two speakers dialogue
  python gemini_tts.py --multi \\
    --speaker "Alice:Kore" --speaker "Bob:Puck" \\
    -t "Alice: How are you today?
Bob: I'm doing great, thanks!"

  # With style directions in text
  python gemini_tts.py --multi \\
    --speaker "Host:Charon" --speaker "Guest:Aoede" \\
    -t "Make Host sound professional and Guest sound excited:
Host: Welcome to the show!
Guest: I'm so thrilled to be here!"

VOICES (30 available):
  Bright:       Zephyr, Autonoe
  Upbeat:       Puck, Laomedeia
  Firm:         Kore, Orus, Alnilam
  Informative:  Charon, Rasalgethi
  Soft/Warm:    Achernar, Sulafat, Vindemiatrix
  Smooth:       Algieba, Despina
  Clear:        Erinome, Iapetus
  Character:    Fenrir (excitable), Enceladus (breathy), 
                Algenib (gravelly), Gacrux (mature)
  Friendly:     Achird, Zubenelgenubi (casual)

STYLE TIPS:
  - Use natural language: "Say angrily:", "Whisper mysteriously:"
  - Specify accents: "British accent from Manchester"
  - Control pace: "Speak slowly and deliberately"
  - Combine: "Say excitedly with a Southern US accent:"
        """
    )
    
    parser.add_argument("--text", "-t", required=True,
                        help="Text to convert to speech")
    parser.add_argument("--voice", "-v", default=DEFAULT_VOICE,
                        choices=list(VOICES.keys()),
                        help=f"Voice to use (default: {DEFAULT_VOICE})")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL,
                        choices=list(MODELS.keys()),
                        help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--style", "-s",
                        help="Style direction prefix (e.g., 'Say cheerfully:')")
    parser.add_argument("--multi", action="store_true",
                        help="Enable multi-speaker mode")
    parser.add_argument("--speaker", action="append",
                        help="Speaker config as 'Name:Voice' (use with --multi)")
    parser.add_argument("--list-voices", "-l", action="store_true",
                        help="List all available voices")
    parser.add_argument("--text-file", "-f",
                        help="Read text from file instead of --text")
    
    args = parser.parse_args()
    
    if args.list_voices:
        print("Available Gemini TTS Voices:")
        print("-" * 50)
        
        # Group by style
        styles = {}
        for voice, style in VOICES.items():
            if style not in styles:
                styles[style] = []
            styles[style].append(voice)
        
        for style, voices in sorted(styles.items()):
            print(f"\n{style}:")
            for voice in voices:
                default = " (default)" if voice == DEFAULT_VOICE else ""
                print(f"  {voice}{default}")
        return
    
    # Read text from file if specified
    text = args.text
    if args.text_file:
        try:
            with open(args.text_file, "r") as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    
    print("=" * 60)
    print("Google Gemini TTS - Text-to-Speech Generation")
    print("=" * 60)
    print()
    
    if args.multi:
        # Multi-speaker mode
        if not args.speaker or len(args.speaker) < 2:
            print("Error: Multi-speaker mode requires at least 2 --speaker args", file=sys.stderr)
            print("Example: --speaker 'Alice:Kore' --speaker 'Bob:Puck'", file=sys.stderr)
            sys.exit(1)
        
        # Parse speaker configs
        speakers = []
        for s in args.speaker:
            if ":" not in s:
                print(f"Error: Speaker format must be 'Name:Voice', got: {s}", file=sys.stderr)
                sys.exit(1)
            name, voice = s.split(":", 1)
            speakers.append((name.strip(), voice.strip()))
        
        print(f"Mode: Multi-speaker ({len(speakers)} speakers)")
        for name, voice in speakers:
            print(f"  {name}: {voice} ({VOICES.get(voice, '?')})")
        print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
        print()
        
        result = generate_speech_multi(text, speakers, args.model)
    else:
        # Single-speaker mode
        print(f"Voice: {args.voice} ({VOICES.get(args.voice, '')})")
        print(f"Model: {MODELS.get(args.model, args.model)}")
        if args.style:
            print(f"Style: {args.style}")
        print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
        print()
        
        result = generate_speech_single(text, args.voice, args.model, args.style)
    
    if "error" in result:
        print(f"\n❌ Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✅ Speech generated successfully!")
        print(f"   File: {result['file']}")
        print(f"   Format: {result['sample_rate']}Hz, {result['channels']}ch WAV")
        import json
        print()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
